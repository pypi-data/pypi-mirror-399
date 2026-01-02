from collections.abc import (
    Callable,
)
from dataclasses import (
    dataclass,
)
from enum import (
    Enum,
)

from fluidattacks_etl_utils.date_range import (
    DateRange,
)
from fluidattacks_etl_utils.typing import (
    Dict,
    Tuple,
)
from fa_purity import (
    Cmd,
    FrozenList,
    Maybe,
    Stream,
    Unsafe,
)
from fa_purity.date_time import (
    DatetimeUTC,
)
from fa_purity.json import (
    JsonObj,
    JsonValueFactory,
    Primitive,
    Unfolder,
)
from pure_requests.basic import (
    Endpoint,
)

TIMEDOCTOR_API = Endpoint("https://api2.timedoctor.com")


def relative_endpoint(relative: str) -> Endpoint:
    return Endpoint(TIMEDOCTOR_API.raw.rstrip("/") + "/" + relative.lstrip("/"))


def new_json(raw: Dict[str, Primitive]) -> JsonObj:
    return (
        Unfolder.to_json(JsonValueFactory.from_dict(raw))
        .alt(Unsafe.raise_exception)
        .to_union()
    )


@dataclass(frozen=True)
class CompanyId:
    company: str


@dataclass(frozen=True)
class CompanyName:
    name: str


@dataclass(frozen=True)
class DeviceId:
    device: str


@dataclass(frozen=True)
class TaskId:
    task: str


@dataclass(frozen=True)
class TaskName:
    name: str


@dataclass(frozen=True)
class UserId:
    user_id: str


@dataclass(frozen=True)
class UserName:
    name: str


@dataclass(frozen=True)
class ProjectId:
    project_id: str


@dataclass(frozen=True)
class ProjectName:
    name: str


class FileEntity(Enum):
    FILE = "FILE"
    SCREENSHOT = "SCREENSHOT"
    VIDEO = "VIDEO"


@dataclass(frozen=True, kw_only=True)
class MetaObj:
    blur: Maybe[bool]
    clicks: Maybe[int]
    movements: Maybe[int]
    keys: Maybe[int]
    period: Maybe[int]
    created_at: Maybe[DatetimeUTC]
    project: Maybe[ProjectId]
    task_id: Maybe[TaskId]
    obj_type: Maybe[str]


@dataclass(frozen=True)
class ComputerActivity:
    user: UserId
    date: DatetimeUTC
    device: DeviceId
    file_index: str
    mime_type: str
    deleted: bool
    avg_activity: Maybe[int]
    entity: FileEntity
    meta: Maybe[MetaObj]


class WorklogMode(Enum):
    OFFLINE = "offline"
    OFFCOMPUTER = "offcomputer"
    COMPUTER = "computer"
    MOBILE = "mobile"
    MANUAL = "manual"
    BREAK = "break"
    PAID_BREAK = "paidbreak"
    UNPAID_BREAK = "unpaidbreak"
    PAID_LEAVE = "paidleave"
    UNPAID_LEAVE = "unpaidleave"


@dataclass(frozen=True)
class WorklogId:
    task_id: TaskId
    task_name: TaskName
    project_id: ProjectId
    project: ProjectName
    device: DeviceId
    user: UserId


@dataclass(frozen=True)
class Worklog:
    worklog_id: WorklogId
    mode: WorklogMode
    start: DatetimeUTC
    time: float


@dataclass(frozen=True)
class ApiClient:
    get_token_companies_id: Cmd[FrozenList[Tuple[CompanyId, CompanyName]]]
    get_users_id: Callable[[CompanyId], Stream[FrozenList[Tuple[UserId, UserName]]]]
    get_projects_id: Callable[
        [CompanyId], Stream[FrozenList[Tuple[ProjectId, ProjectName]]]
    ]
    get_activity: Callable[
        [CompanyId, UserId, DateRange], Stream[FrozenList[ComputerActivity]]
    ]
    get_worklogs: Callable[[CompanyId, UserId, DateRange], Stream[FrozenList[Worklog]]]
