"""Tests for MizbanCloudClient."""

import pytest
from mizbancloud import MizbanCloudClient, MizbanCloudConfig


class TestMizbanCloudClient:
    """Tests for the main client class."""

    def test_client_creation_default(self):
        """Test client creation with defaults."""
        client = MizbanCloudClient()
        assert client is not None
        assert client.auth is not None
        assert client.cdn is not None
        assert client.cloud is not None
        assert client.statics is not None
        client.close()

    def test_client_creation_with_config(self):
        """Test client creation with custom config."""
        config = MizbanCloudConfig(
            base_url="https://custom.api.com",
            timeout=60,
            language="fa",
        )
        client = MizbanCloudClient(config)
        assert client.get_language() == "fa"
        client.close()

    def test_set_token(self):
        """Test setting API token."""
        client = MizbanCloudClient()
        client.set_token("test-token")
        assert client.get_token() == "test-token"
        assert client.is_authenticated() is True
        client.close()

    def test_is_authenticated_false(self):
        """Test is_authenticated returns False when no token."""
        client = MizbanCloudClient()
        assert client.is_authenticated() is False
        client.close()

    def test_set_language(self):
        """Test setting language."""
        client = MizbanCloudClient()
        client.set_language("fa")
        assert client.get_language() == "fa"
        client.set_language("en")
        assert client.get_language() == "en"
        client.close()

    def test_context_manager(self):
        """Test using client as context manager."""
        with MizbanCloudClient() as client:
            assert client is not None
            client.set_token("test")
            assert client.is_authenticated()
