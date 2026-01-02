"""Unit tests for UserService happy path with mocked client.

Covers conversion and logging path without network calls.
"""

from typing import Any

from numistalib.client import NumistaResponse
from numistalib.services.users.service import UserService

from .conftest import DummyClient, DummyResponse


class UserServiceDummyClient(DummyClient):
    def get(self, url: str, **kwargs: Any) -> NumistaResponse:  # type: ignore[override]
        if url.startswith("/users/") and "/collections" not in url and "/collected_items" not in url:
            return DummyResponse({
                "user": {
                    "id": 42,
                    "username": "tester",
                }
            })  # type: ignore[return-value]
        raise AssertionError(f"Unexpected URL {url}")


def test_get_user_happy_path() -> None:
    service = UserService(UserServiceDummyClient())
    user = service.get_user(42)
    assert user.numista_id == 42
    assert user.username == "tester"
