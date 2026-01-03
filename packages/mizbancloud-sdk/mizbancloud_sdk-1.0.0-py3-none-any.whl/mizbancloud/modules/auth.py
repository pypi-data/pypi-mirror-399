"""MizbanCloud Auth Module."""

from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..http_client import HttpClient


class Auth:
    """Authentication and wallet operations."""

    def __init__(self, http_client: "HttpClient"):
        self._http = http_client

    def set_api_token(self, token: str) -> None:
        """Set the API token."""
        self._http.config.token = token

    def get_api_token(self) -> Optional[str]:
        """Get the current API token."""
        return self._http.config.token

    def clear_api_token(self) -> None:
        """Clear the API token."""
        self._http.config.token = None

    def get_wallet(self) -> Any:
        """Get wallet balance and information."""
        return self._http.get("/api/v1/wallet")
