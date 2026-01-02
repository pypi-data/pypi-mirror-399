from fa_purity import (
    Cmd,
    FrozenDict,
    ResultE,
    cast_exception,
)
from pure_requests.basic import (
    HttpClientFactory,
    Params,
)
from pure_requests.response import (
    handle_status,
)

from fluidattacks_timedoctor_sdk.core import (
    new_json,
    relative_endpoint,
)

from ._core import (
    AuthToken,
)


def revoke(token: AuthToken) -> Cmd[ResultE[None]]:
    headers = new_json({"Authorization": " ".join(["JWT", token.token])})
    client = HttpClientFactory.new_client(None, headers, None)
    return client.get(
        relative_endpoint("api/1.0/logout"),
        Params(FrozenDict({})),
    ).map(
        lambda r: r.alt(cast_exception)
        .bind(lambda s: handle_status(s).alt(cast_exception))
        .map(lambda _: None),
    )
