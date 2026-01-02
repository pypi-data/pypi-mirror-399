import os
from datetime import (
    UTC,
)

import pytest
from fluidattacks_etl_utils.date_range import (
    DateRange,
)
from fluidattacks_etl_utils.typing import (
    Tuple,
)
from fa_purity import (
    Cmd,
    FrozenList,
    PureIterFactory,
    StreamTransform,
    Unsafe,
)
from fa_purity.date_time import (
    DatetimeFactory,
    RawDatetime,
)

from fluidattacks_timedoctor_sdk import (
    LOG,
)
from fluidattacks_timedoctor_sdk.auth import (
    AuthClientFactory,
    Credentials,
)
from fluidattacks_timedoctor_sdk.client import (
    new_api_client,
)
from fluidattacks_timedoctor_sdk.core import (
    CompanyId,
    CompanyName,
    ComputerActivity,
    UserId,
    UserName,
)

get_test_company = Cmd.wrap_impure(lambda: CompanyId(os.environ["TIMEDOCTOR_COMPANY"]))
get_test_user = Cmd.wrap_impure(lambda: UserId(os.environ["TIMEDOCTOR_COMPANY_USER"]))


def _assert_companies(companies: FrozenList[Tuple[CompanyId, CompanyName]]) -> None:
    assert len(companies) > 0  # noqa: S101


get_token = (
    AuthClientFactory.new()
    .new_token(
        Credentials(os.environ["TIMEDOCTOR_USER"], os.environ["TIMEDOCTOR_PASSWD"])
    )
    .map(lambda r: r.alt(Unsafe.raise_exception).to_union())
)


def test_get_companies() -> None:
    cmd: Cmd[None] = get_token.bind(
        lambda t: new_api_client(LOG, t).get_token_companies_id.map(_assert_companies),
    )
    with pytest.raises(SystemExit):
        cmd.compute()


def _assert_users(items: FrozenList[Tuple[UserId, UserName]]) -> Cmd[None]:
    assert items  # noqa: S101
    return Cmd.wrap_value(None)


def test_get_users() -> None:
    cmd: Cmd[None] = get_token.bind(
        lambda t: get_test_company.bind(
            lambda company: new_api_client(LOG, t)
            .get_users_id(
                company,
            )
            .transform(
                lambda s: StreamTransform.chain(s.map(PureIterFactory.from_list))
            )
            .to_list()
            .bind(_assert_users),
        ),
    )
    with pytest.raises(SystemExit):
        cmd.compute()


def _test_range() -> DateRange:
    from_date = (
        DatetimeFactory.new_utc(
            RawDatetime(
                year=2024,
                month=12,
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
                time_zone=UTC,
            ),
        )
        .alt(Unsafe.raise_exception)
        .to_union()
    )
    to_date = (
        DatetimeFactory.new_utc(
            RawDatetime(
                year=2024,
                month=12,
                day=6,
                hour=12,
                minute=0,
                second=0,
                microsecond=0,
                time_zone=UTC,
            ),
        )
        .alt(Unsafe.raise_exception)
        .to_union()
    )
    return DateRange.new(from_date, to_date).alt(Unsafe.raise_exception).to_union()


def _assert_activity(items: ComputerActivity) -> Cmd[None]:
    assert items  # noqa: S101
    return Cmd.wrap_value(None)


def test_get_activity() -> None:
    cmd: Cmd[None] = get_token.bind(
        lambda t: get_test_company.bind(
            lambda company: new_api_client(LOG, t)
            .get_users_id(
                company,
            )
            .transform(
                lambda s: StreamTransform.chain(s.map(PureIterFactory.from_list))
            )
            .map(
                lambda u: new_api_client(LOG, t)
                .get_activity(
                    company,
                    u[0],
                    _test_range(),
                )
                .transform(
                    lambda s: StreamTransform.chain(s.map(PureIterFactory.from_list))
                )
                .map(_assert_activity)
                .transform(StreamTransform.consume),
            )
            .transform(StreamTransform.consume),
        ),
    )
    with pytest.raises(SystemExit):
        cmd.compute()
