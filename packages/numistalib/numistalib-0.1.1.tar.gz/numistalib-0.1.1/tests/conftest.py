"""Pytest configuration and fixtures for numistalib tests."""

from unittest.mock import Mock

import pytest

from numistalib.client import NumistaApiClient
from numistalib.config import Settings


@pytest.fixture
def mock_settings() -> Settings:
    """Provide test settings with mock API key."""
    return Settings(api_key="test_api_key_12345")


@pytest.fixture
def mock_client() -> Mock:
    """Provide a mock API client."""
    return Mock(spec=NumistaApiClient)


