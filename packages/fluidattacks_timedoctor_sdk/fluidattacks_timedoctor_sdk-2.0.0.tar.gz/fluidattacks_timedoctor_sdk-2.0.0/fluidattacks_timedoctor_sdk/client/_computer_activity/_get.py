import inspect
from logging import (
    Logger,
)

from fluidattacks_etl_utils.bug import (
    Bug,
)
from fluidattacks_etl_utils.date_range import (
    DateRange,
)
from fluidattacks_etl_utils.paginate import (
    cursor_pagination,
)
from fa_purity import (
    Cmd,
    Coproduct,
    FrozenDict,
    FrozenList,
    Maybe,
    PureIterFactory,
    Result,
    ResultE,
    Stream,
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
    DataPage,
    decode_data,
    decode_page,
    with_retry_handler,
)
from fluidattacks_timedoctor_sdk.core import (
    CompanyId,
    ComputerActivity,
    UserId,
    new_json,
    relative_endpoint,
)

from ._decode import (
    decode_activities,
)


def _decode_data(
    data: Coproduct[JsonObj, FrozenList[JsonObj]],
) -> ResultE[DataPage[FrozenList[ComputerActivity]]]:
    return data.map(
        lambda j: decode_page(j, lambda v: decode_data(v, decode_activities)),
        lambda _: Result.failure(ValueError("Expected json but got a list")).alt(
            cast_exception
        ),
    )


def _decode_response(
    response: Response,
) -> ResultE[DataPage[FrozenList[ComputerActivity]]]:
    return json_decode(response).alt(cast_exception).bind(_decode_data)


def _get_page(
    client: HttpClient,
    company: CompanyId,
    user: UserId,
    dates: DateRange,
    page_id: Maybe[str],
) -> Cmd[ResultE[DataPage[FrozenList[ComputerActivity]]]]:
    get_raw_page = client.get(
        relative_endpoint("api/1.0/files/screenshot"),
        Params(
            FrozenDict(
                {
                    "company": JsonValue.from_primitive(
                        JsonPrimitive.from_str(company.company)
                    ),
                    "user": JsonValue.from_primitive(
                        JsonPrimitive.from_str(user.user_id)
                    ),
                    "from": JsonValue.from_primitive(
                        JsonPrimitive.from_str(dates.from_date.date_time.isoformat()),
                    ),
                    "to": JsonValue.from_primitive(
                        JsonPrimitive.from_str(dates.to_date.date_time.isoformat()),
                    ),
                }
                | page_id.map(
                    lambda p: {
                        "page": JsonValue.from_primitive(JsonPrimitive.from_str(p))
                    },
                ).value_or({}),
            ),
        ),
    )
    return with_retry_handler(get_raw_page, 10).map(lambda r: r.bind(_decode_response))


def get_activity(
    log: Logger,
    token: AuthToken,
    company: CompanyId,
    user: UserId,
    dates: DateRange,
) -> Stream[FrozenList[ComputerActivity]]:
    headers = new_json({"Authorization": " ".join(["JWT", token.token])})
    client = HttpClientFactory.new_client(None, headers, None)
    return cursor_pagination(
        lambda p: Cmd.wrap_impure(
            lambda: log.info(
                "API: get_activity(%s, user=%s, dates=%s, page=%s)",
                company,
                user,
                dates,
                p,
            ),
        )
        + _get_page(client, company, user, dates, p)
        .map(
            lambda r: Bug.assume_success(
                "get_activity",
                inspect.currentframe(),
                (),
                r,
            ),
        )
        .map(
            lambda d: (d.items, d.next_page),
        ),
    ).map(
        lambda i: PureIterFactory.from_list(i)
        .bind(lambda x: PureIterFactory.from_list(x))
        .to_list(),
    )
