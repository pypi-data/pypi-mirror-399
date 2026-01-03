import inspect
from logging import (
    Logger,
)

from dateutil.relativedelta import (
    relativedelta,
)
from fluidattacks_etl_utils.bug import (
    Bug,
)
from fluidattacks_etl_utils.date_range import (
    DateRange,
    split_date_range,
)
from fa_purity import (
    Cmd,
    Coproduct,
    FrozenDict,
    FrozenList,
    PureIterFactory,
    PureIterTransform,
    Result,
    ResultE,
    Stream,
    StreamFactory,
    cast_exception,
)
from fa_purity.json import (
    JsonObj,
    JsonPrimitive,
    JsonValue,
)
from pure_requests.basic import (
    HttpClient,
    HttpClientFactory,
    Params,
)
from pure_requests.response import (
    json_decode,
)
from requests import (
    Response,
)

from fluidattacks_timedoctor_sdk.auth import (
    AuthToken,
)
from fluidattacks_timedoctor_sdk.client._common import (
    decode_data_one_item,
    with_retry_handler,
)
from fluidattacks_timedoctor_sdk.core import (
    CompanyId,
    UserId,
    Worklog,
    new_json,
    relative_endpoint,
)

from ._decode import (
    decode_worklog,
)


def _decode_data(
    data: Coproduct[JsonObj, FrozenList[JsonObj]],
) -> ResultE[FrozenList[Worklog]]:
    return data.map(
        lambda j: decode_data_one_item(j, decode_worklog),
        lambda _: Result.failure(ValueError("Expected json but got a list")).alt(
            cast_exception
        ),
    ).map(
        lambda i: PureIterTransform.filter_maybe(PureIterFactory.from_list(i)).to_list()
    )


def _decode_response(response: Response) -> ResultE[FrozenList[Worklog]]:
    return json_decode(response).alt(cast_exception).bind(_decode_data)


def _get_worklog(
    log: Logger,
    client: HttpClient,
    company: CompanyId,
    user: UserId,
    dates: DateRange,
) -> Cmd[ResultE[FrozenList[Worklog]]]:
    msg = Cmd.wrap_impure(
        lambda: log.info(
            "API: get_worklog(%s, user=%s, dates=%s)",
            company,
            user,
            dates,
        ),
    )
    get_raw = client.get(
        relative_endpoint("api/1.0/activity/worklog"),
        Params(
            FrozenDict(
                {
                    "company": JsonValue.from_primitive(
                        JsonPrimitive.from_str(company.company)
                    ),
                    "user": JsonValue.from_primitive(
                        JsonPrimitive.from_str(user.user_id)
                    ),
                    "detail": JsonValue.from_primitive(JsonPrimitive.from_bool(True)),
                    "task-project-names": JsonValue.from_primitive(
                        JsonPrimitive.from_bool(True)
                    ),
                    "from": JsonValue.from_primitive(
                        JsonPrimitive.from_str(dates.from_date.date_time.isoformat()),
                    ),
                    "to": JsonValue.from_primitive(
                        JsonPrimitive.from_str(dates.to_date.date_time.isoformat()),
                    ),
                },
            ),
        ),
    )
    return msg + with_retry_handler(get_raw, 10).map(lambda r: r.bind(_decode_response))


def get_worklog(
    log: Logger,
    token: AuthToken,
    company: CompanyId,
    user: UserId,
    dates: DateRange,
) -> Stream[FrozenList[Worklog]]:
    headers = new_json({"Authorization": " ".join(["JWT", token.token])})
    client = HttpClientFactory.new_client(None, headers, None)
    return (
        split_date_range(dates, relativedelta(days=5))
        .map(lambda d: _get_worklog(log, client, company, user, d))
        .transform(StreamFactory.from_commands)
        .map(
            lambda r: Bug.assume_success(
                "get_worklog_decode",
                inspect.currentframe(),
                (),
                r,
            ),
        )
    )
