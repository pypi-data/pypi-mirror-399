from fa_purity import Coproduct, Unsafe
from fa_purity.json import JsonValueFactory, Unfolder

from fluidattacks_timedoctor_sdk.client._worklog._get import _decode_data


def test_ignore_no_task() -> None:
    raw = {
        "data": [
            [
                {
                    "start": "2025-01-01T11:22:33.000Z",
                    "time": 10,
                    "mode": "computer",
                    "userId": "123",
                    "deviceId": "222",
                },
            ],
        ],
    }
    raw_json = (
        JsonValueFactory.from_any(raw)
        .bind(Unfolder.to_json)
        .alt(Unsafe.raise_exception)
        .to_union()
    )
    item = _decode_data(Coproduct.inl(raw_json)).alt(Unsafe.raise_exception).to_union()
    assert item == ()
