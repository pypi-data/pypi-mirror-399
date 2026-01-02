import inspect

from fluidattacks_etl_utils import (
    decode,
    smash,
)
from fluidattacks_etl_utils.bug import (
    Bug,
)
from fa_purity import (
    FrozenList,
    Result,
    ResultE,
    cast_exception,
)
from fa_purity.date_time import (
    DatetimeUTC,
)
from fa_purity.json import (
    JsonObj,
    JsonPrimitiveUnfolder,
    JsonUnfolder,
    JsonValue,
    Unfolder,
)

from fluidattacks_timedoctor_sdk.core import (
    ComputerActivity,
    DeviceId,
    FileEntity,
    MetaObj,
    ProjectId,
    TaskId,
    UserId,
)


def _to_str(value: JsonValue) -> ResultE[str]:
    return Unfolder.to_primitive(value).bind(JsonPrimitiveUnfolder.to_str)


def _to_int(value: JsonValue) -> ResultE[int]:
    return Unfolder.to_primitive(value).bind(JsonPrimitiveUnfolder.to_int)


def _to_bool(value: JsonValue) -> ResultE[bool]:
    return Unfolder.to_primitive(value).bind(JsonPrimitiveUnfolder.to_bool)


def decode_meta_obj(data: JsonObj) -> ResultE[MetaObj]:
    group_1 = smash.smash_result_5(
        JsonUnfolder.optional(
            data,
            "blur",
            _to_bool,
        ),
        JsonUnfolder.optional(data, "clicks", _to_int),
        JsonUnfolder.optional(data, "movements", _to_int),
        JsonUnfolder.optional(data, "keys", _to_int),
        JsonUnfolder.optional(data, "period", _to_int),
    )
    group_2 = smash.smash_result_4(
        JsonUnfolder.optional(
            data,
            "created_at",
            lambda v: _to_str(v).bind(decode.to_datetime_utc),
        ),
        JsonUnfolder.optional(data, "project", lambda v: _to_str(v).map(ProjectId)),
        JsonUnfolder.optional(data, "task_id", lambda v: _to_str(v).map(TaskId)),
        JsonUnfolder.optional(data, "obj_type", _to_str),
    )
    return group_1.bind(
        lambda g1: group_2.map(
            lambda g2: MetaObj(
                blur=g1[0],
                clicks=g1[1],
                movements=g1[2],
                keys=g1[3],
                period=g1[4],
                created_at=g2[0],
                project=g2[1],
                task_id=g2[2],
                obj_type=g2[3],
            ),
        ),
    )


def decode_file_entity(raw: str) -> ResultE[FileEntity]:
    try:
        return Result.success(FileEntity(raw.upper()))
    except ValueError as err:
        return Result.failure(err).alt(cast_exception)


def _decode_activity(
    user: UserId,
    date: DatetimeUTC,
    device: DeviceId,
    numbers_item: JsonObj,
) -> ResultE[ComputerActivity]:
    group_1 = smash.smash_result_5(
        JsonUnfolder.require(
            numbers_item,
            "number",
            _to_str,
        ),
        JsonUnfolder.require(numbers_item, "mime", _to_str),
        JsonUnfolder.require(numbers_item, "deleted", _to_bool),
        JsonUnfolder.optional(numbers_item, "avgActivity", _to_int),
        JsonUnfolder.require(
            numbers_item,
            "entity",
            lambda v: _to_str(v).bind(decode_file_entity),
        ),
    )
    _meta = JsonUnfolder.optional(
        numbers_item,
        "meta",
        lambda v: Unfolder.to_json(v).bind(decode_meta_obj),
    )
    return group_1.bind(
        lambda g1: _meta.map(
            lambda meta: ComputerActivity(
                user=user,
                date=date,
                device=device,
                file_index=g1[0],
                mime_type=g1[1],
                deleted=g1[2],
                avg_activity=g1[3],
                entity=g1[4],
                meta=meta,
            ),
        ),
    )


def decode_activities(data: JsonObj) -> ResultE[FrozenList[ComputerActivity]]:
    group_1 = smash.smash_result_3(
        JsonUnfolder.require(
            data,
            "userId",
            lambda v: _to_str(v).map(UserId),
        ),
        JsonUnfolder.require(
            data,
            "date",
            lambda v: _to_str(v).bind(decode.to_datetime_utc),
        ),
        JsonUnfolder.require(
            data,
            "deviceId",
            lambda v: _to_str(v).map(DeviceId),
        ),
    )
    return group_1.bind(
        lambda g1: JsonUnfolder.require(
            data,
            "numbers",
            lambda v: Unfolder.to_list_of(
                v,
                lambda j: Unfolder.to_json(j).bind(
                    lambda v2: _decode_activity(g1[0], g1[1], g1[2], v2),
                ),
            ),
        ),
    ).alt(
        lambda e: Bug.new(
            "decode_activities",
            inspect.currentframe(),
            e,
            (JsonUnfolder.dumps(data),),
        ),
    )
