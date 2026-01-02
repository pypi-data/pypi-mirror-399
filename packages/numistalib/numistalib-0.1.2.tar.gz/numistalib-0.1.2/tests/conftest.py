"""Pytest configuration and fixtures for numistalib tests."""

from typing import Any
from unittest.mock import Mock

import pytest

from numistalib.client import NumistaApiClient, NumistaResponse
from numistalib.config import Settings


class DummyResponse:
    """Mock response object for testing services without network calls."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data
        self.cached_indicator = "💾"

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._data


class DummyClient:
    """Mock client for testing services without network calls."""

    def get(self, url: str, **kwargs: Any) -> NumistaResponse:  # type: ignore[override]
        raise NotImplementedError("Subclass must implement get() for specific test cases")

    def post(self, url: str, **kwargs: Any) -> NumistaResponse:  # type: ignore[override]
        raise NotImplementedError("Subclass must implement post() for specific test cases")

    def patch(self, url: str, **kwargs: Any) -> NumistaResponse:  # type: ignore[override]
        raise NotImplementedError("Subclass must implement patch() for specific test cases")

    def put(self, url: str, **kwargs: Any) -> NumistaResponse:  # type: ignore[override]
        raise NotImplementedError("Subclass must implement put() for specific test cases")

    def delete(self, url: str, **kwargs: Any) -> NumistaResponse:  # type: ignore[override]
        raise NotImplementedError("Subclass must implement delete() for specific test cases")


@pytest.fixture
def mock_settings() -> Settings:
    """Provide test settings with mock API key."""
    return Settings(api_key="test_api_key_12345")


@pytest.fixture
def mock_client() -> Mock:
    """Provide a mock API client."""
    return Mock(spec=NumistaApiClient)


@pytest.fixture
def mock_client_factory() -> type[NumistaApiClient]:
    """Provide a factory for creating mock sync clients."""

    class MockNumistaApiClient(NumistaApiClient):
        """Mock client that doesn't make real HTTP requests."""

        def __init__(self, settings: Settings) -> None:
            """Initialize without creating real HTTP client."""
            self.settings = settings
            self._client = Mock()

        def __enter__(self) -> "MockNumistaApiClient":
            """Context manager entry."""
            return self

        def __exit__(self, *args: object) -> None:
            """Context manager exit."""
            pass

        def get(self, *args: object, **kwargs: object) -> Mock:
            """Mock GET request."""
            return Mock()

        def post(self, *args: object, **kwargs: object) -> Mock:
            """Mock POST request."""
            return Mock()

    return MockNumistaApiClient


@pytest.fixture
def mock_async_client_factory() -> type[NumistaApiClient]:
    """Provide a factory for creating mock async clients."""

    class MockAsyncNumistaApiClient(NumistaApiClient):
        """Mock async client that doesn't make real HTTP requests."""

        def __init__(self, settings: Settings) -> None:
            """Initialize without creating real HTTP client."""
            self.settings = settings
            self._client = Mock()

        async def __aenter__(self) -> "MockAsyncNumistaApiClient":
            """Async context manager entry."""
            return self

        async def __aexit__(self, *args: object) -> None:
            """Async context manager exit."""
            pass

        async def get_async(self, *args: object, **kwargs: object) -> Mock:
            """Mock async GET request."""
            return Mock()

        async def post_async(self, *args: object, **kwargs: object) -> Mock:
            """Mock async POST request."""
            return Mock()

    return MockAsyncNumistaApiClient
