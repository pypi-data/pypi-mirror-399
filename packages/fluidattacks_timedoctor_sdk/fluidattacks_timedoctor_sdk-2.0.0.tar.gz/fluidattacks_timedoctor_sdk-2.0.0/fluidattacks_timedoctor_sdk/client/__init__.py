from logging import (
    Logger,
)

from fluidattacks_timedoctor_sdk.auth import (
    AuthToken,
)
from fluidattacks_timedoctor_sdk.core import (
    ApiClient,
)

from . import (
    _computer_activity,
    _get_companies,
    _get_projects,
    _get_users,
    _worklog,
)


def new_api_client(log: Logger, token: AuthToken) -> ApiClient:
    return ApiClient(
        _get_companies.get_token_companies(log, token),
        lambda c: _get_users.get_users(log, token, c),
        lambda c: _get_projects.get_projects(log, token, c),
        lambda c, u, d: _computer_activity.get_activity(log, token, c, u, d),
        lambda c, u, d: _worklog.get_worklog(log, token, c, u, d),
    )
