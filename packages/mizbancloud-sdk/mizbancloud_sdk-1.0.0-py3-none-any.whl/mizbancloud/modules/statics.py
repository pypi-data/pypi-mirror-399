"""MizbanCloud Statics Module."""

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..http_client import HttpClient


class Statics:
    """Static catalog data for server creation."""

    def __init__(self, http_client: "HttpClient"):
        self._http = http_client

    def list_datacenters(self) -> Any:
        """List available datacenters."""
        return self._http.get("/api/v1/cloud/catalog/datacenters")

    def list_operating_systems(self) -> Any:
        """List available operating systems."""
        return self._http.get("/api/v1/cloud/catalog/images")

    def get_cache_times(self) -> Any:
        """Get cache time options."""
        return self._http.get("/api/v1/statics/cache-times")

    def get_sliders(self) -> Any:
        """Get slider configurations."""
        return self._http.get("/api/v1/statics/sliders")
