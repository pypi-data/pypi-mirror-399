import inspect
from logging import (
    Logger,
)

from fluidattacks_etl_utils import (
    smash,
)
from fluidattacks_etl_utils.bug import (
    Bug,
)
from fluidattacks_etl_utils.typing import (
    Tuple,
)
from fa_purity import (
    Cmd,
    Coproduct,
    FrozenDict,
    FrozenList,
    Result,
    ResultE,
    cast_exception,
)
from fa_purity.json import (
    JsonObj,
    JsonPrimitiveUnfolder,
    JsonUnfolder,
    Unfolder,
)
from pure_requests.basic import (
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
    CompanyName,
    new_json,
    relative_endpoint,
)


def _decode_company(data: JsonObj) -> ResultE[Tuple[CompanyId, CompanyName]]:
    _id = JsonUnfolder.require(
        data,
        "id",
        lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_str),
    ).map(CompanyId)
    _name = JsonUnfolder.require(
        data,
        "name",
        lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_str),
    ).map(CompanyName)
    return smash.smash_result_2(
        _id,
        _name,
    )


def _decode_companies_id(
    data: JsonObj,
) -> ResultE[FrozenList[Tuple[CompanyId, CompanyName]]]:
    return JsonUnfolder.require(
        data,
        "companies",
        lambda v: Unfolder.to_list_of(
            v, lambda j: Unfolder.to_json(j).bind(_decode_company)
        ),
    )


def _decode_json_data(
    raw: JsonObj,
) -> ResultE[FrozenList[Tuple[CompanyId, CompanyName]]]:
    return JsonUnfolder.require(
        raw,
        "data",
        lambda v: Unfolder.to_json(v).bind(_decode_companies_id),
    )


def _decode_data(
    data: Coproduct[JsonObj, FrozenList[JsonObj]],
) -> ResultE[FrozenList[Tuple[CompanyId, CompanyName]]]:
    return data.map(
        _decode_json_data,
        lambda _: Result.failure(ValueError("Expected json but got a list")).alt(
            cast_exception
        ),
    )


def _decode_response(
    response: Response,
) -> ResultE[FrozenList[Tuple[CompanyId, CompanyName]]]:
    return json_decode(response).alt(cast_exception).bind(_decode_data)


def get_token_companies(
    log: Logger,
    token: AuthToken,
) -> Cmd[FrozenList[Tuple[CompanyId, CompanyName]]]:
    headers = new_json({"Authorization": " ".join(["JWT", token.token])})
    client = HttpClientFactory.new_client(None, headers, None)
    msg = Cmd.wrap_impure(lambda: log.info("API: get_token_companies"))
    get_token_response = client.get(
        relative_endpoint("api/1.0/authorization"),
        Params(FrozenDict({})),
    )
    return msg + (
        with_retry_handler(get_token_response, 3)
        .map(lambda r: r.bind(_decode_response))
        .map(
            lambda r: Bug.assume_success("get_companies", inspect.currentframe(), (), r)
        )
    )
