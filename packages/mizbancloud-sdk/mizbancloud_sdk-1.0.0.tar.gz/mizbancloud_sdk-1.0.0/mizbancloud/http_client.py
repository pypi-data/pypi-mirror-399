"""MizbanCloud HTTP Client."""

from typing import Any, Dict, Optional
import requests

from .config import MizbanCloudConfig
from .exceptions import MizbanCloudException


class HttpClient:
    """HTTP client for MizbanCloud API requests."""

    def __init__(self, config: MizbanCloudConfig):
        self._config = config
        self._session = requests.Session()

    @property
    def config(self) -> MizbanCloudConfig:
        """Get configuration."""
        return self._config

    def _get_headers(self) -> Dict[str, str]:
        """Build request headers."""
        headers = {
            "Accept": "application/json",
            "Accept-Language": self._config.language,
            **self._config.headers,
        }
        if self._config.token:
            headers["Authorization"] = f"Bearer {self._config.token}"
        return headers

    def _handle_response(self, response: requests.Response) -> Any:
        """Process API response."""
        try:
            data = response.json()
        except ValueError:
            data = None

        if response.status_code >= 400:
            message = "API request failed"
            fields = {}
            invalid_fields = []
            missing_fields = []

            if isinstance(data, dict):
                message = data.get("message", message)
                if "errors" in data:
                    errors = data["errors"]
                    if isinstance(errors, dict):
                        fields = errors
                    elif isinstance(errors, list):
                        for err in errors:
                            if isinstance(err, dict):
                                if err.get("type") == "invalid":
                                    invalid_fields.append(err.get("field", ""))
                                elif err.get("type") == "missing":
                                    missing_fields.append(err.get("field", ""))

            raise MizbanCloudException(
                message=message,
                status_code=response.status_code,
                fields=fields,
                invalid_fields=invalid_fields,
                missing_fields=missing_fields,
                response=data,
            )

        return data

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make GET request."""
        url = f"{self._config.base_url}{endpoint}"
        response = self._session.get(
            url,
            params=params,
            headers=self._get_headers(),
            timeout=self._config.timeout,
        )
        return self._handle_response(response)

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Make POST request."""
        url = f"{self._config.base_url}{endpoint}"
        response = self._session.post(
            url,
            data=data,
            headers=self._get_headers(),
            timeout=self._config.timeout,
        )
        return self._handle_response(response)

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Make PUT request."""
        url = f"{self._config.base_url}{endpoint}"
        response = self._session.put(
            url,
            data=data,
            headers=self._get_headers(),
            timeout=self._config.timeout,
        )
        return self._handle_response(response)

    def delete(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Make DELETE request."""
        url = f"{self._config.base_url}{endpoint}"
        response = self._session.delete(
            url,
            data=data,
            headers=self._get_headers(),
            timeout=self._config.timeout,
        )
        return self._handle_response(response)

    def close(self) -> None:
        """Close the session."""
        self._session.close()
