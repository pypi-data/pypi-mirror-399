from arch_lint.dag import (
    DagMap,
)
from arch_lint.graph import (
    FullPathModule,
)
from fluidattacks_etl_utils.typing import (
    Dict,
    FrozenSet,
    NoReturn,
    TypeVar,
)

_T = TypeVar("_T")


def raise_or_return(item: _T | Exception) -> _T | NoReturn:
    if isinstance(item, Exception):
        raise item
    return item


def _module(path: str) -> FullPathModule | NoReturn:
    return raise_or_return(FullPathModule.from_raw(path))


_dag: Dict[str, tuple[tuple[str, ...] | str, ...]] = {
    "fluidattacks_timedoctor_sdk": (
        "client",
        "auth",
        ("core", "_logger"),
    ),
    "fluidattacks_timedoctor_sdk.client": (
        (
            "_get_users",
            "_get_projects",
            "_get_companies",
            "_computer_activity",
            "_worklog",
            "_common",
        ),
    ),
    "fluidattacks_timedoctor_sdk.client._computer_activity": (
        "_get",
        "_decode",
    ),
    "fluidattacks_timedoctor_sdk.client._worklog": (
        "_get",
        "_decode",
    ),
    "fluidattacks_timedoctor_sdk.auth": (
        ("_new_token", "_revoke"),
        "_core",
    ),
}


def project_dag() -> DagMap:
    return raise_or_return(DagMap.new(_dag))


def forbidden_allowlist() -> Dict[FullPathModule, FrozenSet[FullPathModule]]:
    _raw: Dict[str, FrozenSet[str]] = {}
    return {_module(k): frozenset(_module(i) for i in v) for k, v in _raw.items()}
