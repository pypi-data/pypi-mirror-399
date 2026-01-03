import inspect
from dataclasses import (
    dataclass,
)
from logging import (
    Logger,
)

from fluidattacks_etl_utils.bug import (
    Bug,
)
from fluidattacks_etl_utils.paginate import (
    cursor_pagination,
)
from fluidattacks_etl_utils.typing import (
    Tuple,
)
from fa_purity import (
    Cmd,
    Coproduct,
    FrozenDict,
    FrozenList,
    Maybe,
    Result,
    ResultE,
    Stream,
    cast_exception,
)
from fa_purity.json import (
    JsonObj,
    JsonPrimitive,
    JsonPrimitiveUnfolder,
    JsonUnfolder,
    JsonValue,
    Unfolder,
)
from pure_requests.basic import (
    HttpClient,
    HttpClientFactory,
    Params,
)
from pure_requests.response import (
    json_decode,
)
from requests import (
    Response,
)

from fluidattacks_timedoctor_sdk.auth import (
    AuthToken,
)
from fluidattacks_timedoctor_sdk.client._common import with_retry_handler
from fluidattacks_timedoctor_sdk.core import (
    CompanyId,
    UserId,
    UserName,
    new_json,
    relative_endpoint,
)


@dataclass(frozen=True)
class _DataPage:
    users: FrozenList[Tuple[UserId, UserName]]
    next_page: Maybe[str]


def _decode_user_id(data: JsonObj) -> ResultE[Tuple[UserId, UserName]]:
    return JsonUnfolder.require(
        data,
        "id",
        lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_str),
    ).bind(
        lambda user_id: JsonUnfolder.require(
            data,
            "name",
            lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_str),
        ).map(lambda name: (UserId(user_id), UserName(name))),
    )


def _decode_next_page(data: JsonObj) -> ResultE[Maybe[str]]:
    return JsonUnfolder.optional(
        data,
        "next",
        lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_str),
    )


def _decode_json_data(raw: JsonObj) -> ResultE[_DataPage]:
    data = JsonUnfolder.require(
        raw,
        "data",
        lambda v: Unfolder.to_list_of(
            v, lambda j: Unfolder.to_json(j).bind(_decode_user_id)
        ),
    )
    page = JsonUnfolder.optional(
        raw,
        "page",
        lambda v: Unfolder.to_json(v).bind(_decode_next_page),
    ).map(lambda m: m.bind(lambda x: x))
    return data.bind(lambda d: page.map(lambda p: _DataPage(d, p)))


def _decode_data(data: Coproduct[JsonObj, FrozenList[JsonObj]]) -> ResultE[_DataPage]:
    return data.map(
        _decode_json_data,
        lambda _: Result.failure(ValueError("Expected json but got a list")).alt(
            cast_exception
        ),
    )


def _decode_response(response: Response) -> ResultE[_DataPage]:
    return json_decode(response).alt(cast_exception).bind(_decode_data)


def _get_users_page(
    client: HttpClient,
    company: CompanyId,
    page_id: Maybe[str],
) -> Cmd[ResultE[_DataPage]]:
    get_response = client.get(
        relative_endpoint("api/1.0/users"),
        Params(
            FrozenDict(
                {
                    "company": JsonValue.from_primitive(
                        JsonPrimitive.from_str(company.company)
                    ),
                }
                | page_id.map(
                    lambda p: {
                        "page": JsonValue.from_primitive(JsonPrimitive.from_str(p))
                    },
                ).value_or({}),
            ),
        ),
    )
    return with_retry_handler(get_response, 3).map(lambda r: r.bind(_decode_response))


def get_users(
    log: Logger,
    token: AuthToken,
    company: CompanyId,
) -> Stream[FrozenList[Tuple[UserId, UserName]]]:
    headers = new_json({"Authorization": " ".join(["JWT", token.token])})
    client = HttpClientFactory.new_client(None, headers, None)
    return cursor_pagination(
        lambda p: Cmd.wrap_impure(
            lambda: log.info("API: get_users(%s, page=%s)", company, p)
        )
        + _get_users_page(client, company, p)
        .map(
            lambda r: Bug.assume_success(
                "get_users",
                inspect.currentframe(),
                (),
                r,
            ),
        )
        .map(
            lambda d: (d.users, d.next_page),
        ),
    )
