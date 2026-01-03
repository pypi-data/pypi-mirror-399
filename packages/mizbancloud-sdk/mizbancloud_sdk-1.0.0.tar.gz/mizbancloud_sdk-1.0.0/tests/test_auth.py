"""Tests for Auth module."""

import pytest
from mizbancloud import MizbanCloudClient
from mizbancloud.modules.auth import Auth


class TestAuthModule:
    """Tests for the Auth module."""

    def test_auth_module_exists(self):
        """Test auth module exists on client."""
        with MizbanCloudClient() as client:
            assert client.auth is not None
            assert isinstance(client.auth, Auth)

    def test_auth_has_4_methods(self):
        """Test auth has at least 4 public methods."""
        methods = [m for m in dir(Auth) if not m.startswith("_")]
        assert len(methods) >= 4

    def test_set_api_token_exists(self):
        """Test set_api_token method exists."""
        assert hasattr(Auth, "set_api_token")
        assert callable(getattr(Auth, "set_api_token"))

    def test_get_api_token_exists(self):
        """Test get_api_token method exists."""
        assert hasattr(Auth, "get_api_token")
        assert callable(getattr(Auth, "get_api_token"))

    def test_clear_api_token_exists(self):
        """Test clear_api_token method exists."""
        assert hasattr(Auth, "clear_api_token")
        assert callable(getattr(Auth, "clear_api_token"))

    def test_get_wallet_exists(self):
        """Test get_wallet method exists."""
        assert hasattr(Auth, "get_wallet")
        assert callable(getattr(Auth, "get_wallet"))

    def test_set_and_get_token(self):
        """Test setting and getting token via auth module."""
        with MizbanCloudClient() as client:
            client.auth.set_api_token("my-token")
            assert client.auth.get_api_token() == "my-token"

    def test_clear_token(self):
        """Test clearing token via auth module."""
        with MizbanCloudClient() as client:
            client.auth.set_api_token("my-token")
            client.auth.clear_api_token()
            assert client.auth.get_api_token() is None
