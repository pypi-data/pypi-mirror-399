import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol, TypedDict
from uuid import UUID

if TYPE_CHECKING:

    class CLIAuthTokens(TypedDict):
        access_token: str

else:
    CLIAuthTokens = dict[str, Any]

try:
    # vitalx.cli_auth is an optional dependency.
    from vitalx.cli_auth import current_tokens

except ModuleNotFoundError:

    def current_tokens(refresh_if_needed: bool = False) -> CLIAuthTokens | None:
        return None


class ExecutorAuth(Protocol):
    def headers(self) -> dict[str, str]:
        ...


@dataclass(frozen=True, eq=True)
class APIKeyAuth(ExecutorAuth):
    api_key: str

    def headers(self) -> dict[str, str]:
        return {"X-Vital-API-Key": self.api_key}


@dataclass(frozen=True, eq=True)
class CLIAuth0Auth(ExecutorAuth):
    team_id: UUID

    def headers(self) -> dict[str, str]:
        tokens = current_tokens(refresh_if_needed=True)
        if not tokens:
            raise RuntimeError("failed to load vitalx-cli auth tokens")

        return {
            "Authorization": "Bearer " + tokens["access_token"],
            "X-Vital-Team-ID": str(self.team_id),
        }


def infer_executor_auth(team_id: UUID, explicit_api_key: str | None = None):
    api_key = explicit_api_key or os.environ.get("VITAL_API_KEY")

    if api_key:
        return APIKeyAuth(api_key=api_key)

    if current_tokens():
        return CLIAuth0Auth(team_id=team_id)

    raise RuntimeError(
        "None of the supported authentication method is available:  Vital API Key, the VITAL_API_KEY env var."
    )
