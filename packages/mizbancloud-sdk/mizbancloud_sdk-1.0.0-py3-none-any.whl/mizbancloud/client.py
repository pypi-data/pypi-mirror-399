"""MizbanCloud SDK Client."""

from typing import Optional

from .config import MizbanCloudConfig
from .http_client import HttpClient
from .modules import Auth, Cdn, Cloud, Statics


class MizbanCloudClient:
    """Main client for interacting with MizbanCloud APIs."""

    def __init__(self, config: Optional[MizbanCloudConfig] = None):
        """Initialize MizbanCloud client.

        Args:
            config: Optional configuration. Uses defaults if not provided.
        """
        self._config = config or MizbanCloudConfig()
        self._http = HttpClient(self._config)

        # Initialize modules
        self._auth = Auth(self._http)
        self._cdn = Cdn(self._http)
        self._cloud = Cloud(self._http)
        self._statics = Statics(self._http)

    @property
    def auth(self) -> Auth:
        """Get Auth module."""
        return self._auth

    @property
    def cdn(self) -> Cdn:
        """Get CDN module."""
        return self._cdn

    @property
    def cloud(self) -> Cloud:
        """Get Cloud module."""
        return self._cloud

    @property
    def statics(self) -> Statics:
        """Get Statics module."""
        return self._statics

    def set_token(self, token: str) -> None:
        """Set API token."""
        self._config.token = token

    def get_token(self) -> Optional[str]:
        """Get current API token."""
        return self._config.token

    def set_language(self, language: str) -> None:
        """Set response language ('en' or 'fa')."""
        self._config.language = language

    def get_language(self) -> str:
        """Get current language."""
        return self._config.language

    def is_authenticated(self) -> bool:
        """Check if client has a token set."""
        return self._config.token is not None

    def close(self) -> None:
        """Close the client and release resources."""
        self._http.close()

    def __enter__(self) -> "MizbanCloudClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
