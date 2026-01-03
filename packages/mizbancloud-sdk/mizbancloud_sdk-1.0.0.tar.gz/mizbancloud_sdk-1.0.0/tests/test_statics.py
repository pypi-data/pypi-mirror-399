"""Tests for Statics module."""

import pytest
from mizbancloud import MizbanCloudClient
from mizbancloud.modules.statics import Statics


class TestStaticsModule:
    """Tests for the Statics module."""

    def test_statics_module_exists(self):
        """Test Statics module exists on client."""
        with MizbanCloudClient() as client:
            assert client.statics is not None
            assert isinstance(client.statics, Statics)

    def test_statics_has_4_methods(self):
        """Test Statics has at least 4 public methods."""
        methods = [m for m in dir(Statics) if not m.startswith("_")]
        assert len(methods) >= 4

    def test_list_datacenters_exists(self):
        """Test list_datacenters method exists."""
        assert hasattr(Statics, "list_datacenters")
        assert callable(getattr(Statics, "list_datacenters"))

    def test_list_operating_systems_exists(self):
        """Test list_operating_systems method exists."""
        assert hasattr(Statics, "list_operating_systems")
        assert callable(getattr(Statics, "list_operating_systems"))

    def test_get_cache_times_exists(self):
        """Test get_cache_times method exists."""
        assert hasattr(Statics, "get_cache_times")
        assert callable(getattr(Statics, "get_cache_times"))

    def test_get_sliders_exists(self):
        """Test get_sliders method exists."""
        assert hasattr(Statics, "get_sliders")
        assert callable(getattr(Statics, "get_sliders"))
