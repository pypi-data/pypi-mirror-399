import datetime

from fa_purity import Coproduct, Unsafe
from fa_purity._core.utils import raise_exception
from fa_purity.date_time import DatetimeUTC
from fa_purity.json import JsonValueFactory, Unfolder

from fluidattacks_timedoctor_sdk.client._worklog._get import _decode_data
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


def test_decode_worklog() -> None:
    raw = {
        "data": [
            [
                {
                    "start": "2025-01-01T11:22:33.000Z",
                    "time": 43200,
                    "mode": "mobile",
                    "userId": "001",
                    "taskId": "666",
                    "taskName": "MaintainTheGames",
                    "projectId": "123",
                    "projectName": "Squid",
                    "deviceId": "66",
                },
                {
                    "start": "2025-01-01T11:22:33.000Z",
                    "time": 86400,
                    "mode": "computer",
                    "userId": "456",
                    "taskId": "1",
                    "taskName": "StopTheGames",
                    "projectId": "123",
                    "projectName": "Squid",
                    "deviceId": "77",
                },
            ],
        ],
    }
    mock_date = datetime.datetime(2025, 1, 1, 11, 22, 33, 0, datetime.UTC)
    worklog_1 = Worklog(
        WorklogId(
            TaskId("666"),
            TaskName("MaintainTheGames"),
            ProjectId("123"),
            ProjectName("Squid"),
            DeviceId("66"),
            UserId("001"),
        ),
        WorklogMode.MOBILE,
        DatetimeUTC.assert_utc(mock_date).alt(raise_exception).to_union(),
        43200,
    )
    worklog_2 = Worklog(
        WorklogId(
            TaskId("1"),
            TaskName("StopTheGames"),
            ProjectId("123"),
            ProjectName("Squid"),
            DeviceId("77"),
            UserId("456"),
        ),
        WorklogMode.COMPUTER,
        DatetimeUTC.assert_utc(mock_date).alt(raise_exception).to_union(),
        86400,
    )
    raw_json = (
        JsonValueFactory.from_any(raw)
        .bind(Unfolder.to_json)
        .alt(Unsafe.raise_exception)
        .to_union()
    )
    item = _decode_data(Coproduct.inl(raw_json)).alt(Unsafe.raise_exception).to_union()
    assert item == (worklog_1, worklog_2)
