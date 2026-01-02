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
    Data,
    HttpClientFactory,
    Params,
)
from pure_requests.response import (
    handle_status,
    json_decode,
)
from requests import (
    Response,
)

from fluidattacks_timedoctor_sdk.core import (
    new_json,
    relative_endpoint,
)

from ._core import (
    AuthToken,
    Credentials,
)


def _encode_creds(creds: Credentials) -> JsonObj:
    return new_json(
        {
            "email": creds.user,
            "password": creds.password,
            "totpCode": "",
            "permissions": "read",
        },
    )


def _decode_json_data(data: JsonObj) -> ResultE[AuthToken]:
    return (
        JsonUnfolder.require(data, "data", Unfolder.to_json)
        .bind(
            lambda j: JsonUnfolder.require(
                j,
                "token",
                lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_str),
            ),
        )
        .map(AuthToken)
    )


def _decode_data(data: Coproduct[JsonObj, FrozenList[JsonObj]]) -> ResultE[AuthToken]:
    return data.map(
        _decode_json_data,
        lambda _: Result.failure(ValueError("Expected json but got a list")).alt(
            cast_exception
        ),
    )


def _decode_response(response: Response) -> ResultE[AuthToken]:
    return json_decode(response).alt(cast_exception).bind(_decode_data)


def get_token(creds: Credentials) -> Cmd[ResultE[AuthToken]]:
    headers = new_json({"Content-Type": "application/json"})
    client = HttpClientFactory.new_client(None, headers, None)
    return client.post(
        relative_endpoint("api/1.0/login"),
        Params(FrozenDict({})),
        Data(_encode_creds(creds)),
    ).map(
        lambda r: r.alt(cast_exception)
        .bind(lambda s: handle_status(s).alt(cast_exception))
        .bind(_decode_response),
    )
