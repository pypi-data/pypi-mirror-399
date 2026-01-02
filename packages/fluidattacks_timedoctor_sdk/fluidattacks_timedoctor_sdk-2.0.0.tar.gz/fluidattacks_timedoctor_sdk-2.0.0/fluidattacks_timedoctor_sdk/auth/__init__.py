from dataclasses import (
    dataclass,
)

from ._core import (
    AuthClient,
    AuthToken,
    Credentials,
)
from ._new_token import (
    get_token,
)
from ._revoke import (
    revoke,
)


@dataclass(frozen=True)
class AuthClientFactory:
    @staticmethod
    def new() -> AuthClient:
        return AuthClient(get_token, revoke)


__all__ = [
    "AuthClient",
    "AuthToken",
    "Credentials",
]
