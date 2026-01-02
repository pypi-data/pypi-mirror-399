from dataclasses import (
    dataclass,
    field,
)

from fluidattacks_etl_utils.typing import (
    Callable,
)
from fa_purity import (
    Cmd,
    ResultE,
)


@dataclass(frozen=True)
class Credentials:
    user: str = field(repr=False)
    password: str = field(repr=False)


@dataclass(frozen=True)
class AuthToken:
    token: str = field(repr=False)


@dataclass(frozen=True)
class AuthClient:
    new_token: Callable[[Credentials], Cmd[ResultE[AuthToken]]]
    revoke_token: Callable[[AuthToken], Cmd[ResultE[None]]]
