from fluidattacks_etl_utils import (
    decode,
    smash,
)
from fa_purity import (
    Maybe,
    Result,
    ResultE,
)
from fa_purity.json import (
    JsonObj,
    JsonPrimitiveUnfolder,
    JsonUnfolder,
    JsonValue,
    Unfolder,
)

from fluidattacks_timedoctor_sdk.core import (
    DeviceId,
    ProjectId,
    ProjectName,
    TaskId,
    TaskName,
    UserId,
    Worklog,
    WorklogId,
    WorklogMode,
)


def _to_str(value: JsonValue) -> ResultE[str]:
    """Decode a `JsonValue` into a possible str."""
    return Unfolder.to_primitive(value).bind(JsonPrimitiveUnfolder.to_str)


def decode_worklog_id(data: JsonObj) -> ResultE[WorklogId]:
    """Decode a `WorklogId` object."""
    group_1 = smash.smash_result_5(
        JsonUnfolder.require(
            data,
            "taskId",
            lambda v: _to_str(v).map(TaskId),
        ),
        JsonUnfolder.optional(
            data,
            "taskName",
            lambda v: _to_str(v).map(TaskName),
        ),
        JsonUnfolder.require(
            data,
            "projectId",
            lambda v: _to_str(v).map(ProjectId),
        ),
        JsonUnfolder.optional(
            data,
            "projectName",
            lambda v: _to_str(v).map(ProjectName),
        ),
        JsonUnfolder.optional(
            data,
            "deviceId",
            lambda v: _to_str(v).map(DeviceId),
        ),
    )
    _user = JsonUnfolder.require(
        data,
        "userId",
        lambda v: _to_str(v).map(UserId),
    )
    return group_1.bind(
        lambda g1: _user.map(
            lambda u: WorklogId(
                g1[0],
                g1[1].value_or(TaskName("")),
                g1[2],
                g1[3].value_or(ProjectName("")),
                g1[4].value_or(DeviceId("")),
                u,
            ),
        ),
    )


def decode_work_log_mode(raw: str) -> ResultE[WorklogMode]:
    """Decode a `WorklogMode` object."""
    try:
        return Result.success(WorklogMode(raw.lower()))
    except ValueError as e:
        return Result.failure(e)


def _decode_worklog(data: JsonObj) -> ResultE[Worklog]:
    """Decode a `Worklog` object."""
    group_1 = smash.smash_result_3(
        JsonUnfolder.require(
            data,
            "mode",
            lambda v: _to_str(v).bind(decode_work_log_mode),
        ),
        JsonUnfolder.require(
            data,
            "start",
            lambda v: _to_str(v).bind(decode.to_datetime_utc),
        ),
        JsonUnfolder.require(
            data,
            "time",
            lambda v: Unfolder.to_primitive(v).bind(
                lambda p: JsonPrimitiveUnfolder.to_float(p).lash(
                    lambda _: JsonPrimitiveUnfolder.to_int(p).map(float),
                ),
            ),
        ),
    )
    _id = decode_worklog_id(data)
    return group_1.bind(
        lambda g1: _id.map(
            lambda i: Worklog(
                i,
                g1[0],
                g1[1],
                g1[2],
            ),
        ),
    )


def decode_worklog(data: JsonObj) -> ResultE[Maybe[Worklog]]:
    """
    Decode a `Worklog` object.

    - If `taskId` key is missing then ignore.
    """
    return (
        Maybe.from_optional(data.get("taskId"))
        .to_result()
        .to_coproduct()
        .map(
            lambda _: _decode_worklog(data).map(Maybe.some),
            lambda _: Result.success(Maybe.empty()),
        )
    )
