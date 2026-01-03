import inspect
import logging
from dataclasses import (
    dataclass,
)

from fluidattacks_etl_utils.bug import (
    Bug,
)
from fluidattacks_etl_utils.typing import (
    Callable,
    Generic,
    TypeVar,
)
from fa_purity import (
    Cmd,
    FrozenList,
    Maybe,
    Result,
    ResultE,
    cast_exception,
)
from fa_purity.json import (
    JsonObj,
    JsonPrimitiveUnfolder,
    JsonUnfolder,
    JsonValue,
    Unfolder,
)
from pure_requests.response import handle_status
from pure_requests.retry import HandledErrorFactory, cmd_if_fail, retry_cmd, sleep_cmd
from requests import HTTPError, RequestException, Response

_T = TypeVar("_T")
LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class DataPage(Generic[_T]):
    items: FrozenList[_T]
    next_page: Maybe[str]


def _one_or_none(items: FrozenList[_T]) -> ResultE[Maybe[_T]]:
    if len(items) == 0:
        return Result.success(Maybe.empty())
    if len(items) == 1:
        return Result.success(Maybe.some(items[0]))
    return Result.failure(
        ValueError(f"Expected only one element but got: {len(items)}")
    ).alt(
        cast_exception,
    )


def _decode_data_item(
    raw: JsonObj, decode: Callable[[JsonValue], ResultE[_T]]
) -> ResultE[_T]:
    return JsonUnfolder.require(
        raw,
        "data",
        decode,
    ).alt(
        lambda e: Bug.new(
            "decode_json_data",
            inspect.currentframe(),
            e,
            (JsonUnfolder.dumps(raw),),
        ),
    )


def decode_data(
    raw: JsonObj, decode: Callable[[JsonObj], ResultE[_T]]
) -> ResultE[FrozenList[_T]]:
    return _decode_data_item(
        raw,
        lambda v: Unfolder.to_list_of(v, lambda j: Unfolder.to_json(j).bind(decode)),
    )


def decode_data_one_item(
    raw: JsonObj,
    decode: Callable[[JsonObj], ResultE[_T]],
) -> ResultE[FrozenList[_T]]:
    empty: ResultE[FrozenList[_T]] = Result.success((), Exception)
    return _decode_data_item(
        raw,
        lambda v: Unfolder.to_list(v)
        .bind(_one_or_none)
        .bind(
            lambda m: m.map(
                lambda v2: Unfolder.to_list_of(
                    v2, lambda j: Unfolder.to_json(j).bind(decode)
                ),
            ).value_or(empty),
        ),
    )


def _decode_next_page(data: JsonObj) -> ResultE[Maybe[str]]:
    return JsonUnfolder.optional(
        data,
        "next",
        lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_str),
    )


def decode_page(
    raw: JsonObj,
    decode: Callable[[JsonObj], ResultE[FrozenList[_T]]],
) -> ResultE[DataPage[_T]]:
    data = decode(raw)
    page = JsonUnfolder.optional(
        raw,
        "page",
        lambda v: Unfolder.to_json(v).bind(_decode_next_page),
    ).map(lambda m: m.bind(lambda x: x))
    return data.bind(lambda d: page.map(lambda p: DataPage(d, p))).alt(
        lambda e: Bug.new(
            "_decode_json_data",
            inspect.currentframe(),
            e,
            (JsonUnfolder.dumps(raw),),
        ),
    )


def with_retry_handler(
    raw_page: Cmd[Result[Response, RequestException]],
    retries: int,
) -> Cmd[ResultE[Response]]:
    error_factory: HandledErrorFactory[HTTPError, Exception] = HandledErrorFactory()
    handled_get_page = raw_page.map(
        lambda r: r.alt(cast_exception)
        .alt(error_factory.unhandled)
        .bind(
            lambda r: handle_status(r).alt(
                lambda e: error_factory.handled(e)
                if e.errno and e.errno >= 500 and e.errno < 600  # noqa: PLR2004
                else error_factory.unhandled(cast_exception(e)),
            ),
        ),
    )
    return retry_cmd(
        handled_get_page,
        lambda i, r: cmd_if_fail(
            r,
            Cmd.wrap_impure(lambda: LOG.info("Error handled i.e. %s", r))
            + sleep_cmd(10 + 60 * (i - 1)),
        ),
        retries,
    )
