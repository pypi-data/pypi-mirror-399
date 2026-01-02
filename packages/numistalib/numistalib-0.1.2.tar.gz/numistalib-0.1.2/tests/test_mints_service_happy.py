"""Unit tests for MintService happy path with mocked client.

Covers get_mints conversion and logging path without network calls.
"""

from typing import Any

from numistalib.client import NumistaResponse
from numistalib.services.mints.service import MintService

from .conftest import DummyClient, DummyResponse


class MintServiceDummyClient(DummyClient):
    def get(self, url: str, **kwargs: Any) -> NumistaResponse:  # type: ignore[override]
        assert url == "/mints"
        return DummyResponse({
            "mints": [
                {
                    "numista_id": 1,
                    "name": "Test Mint",
                    "code": "TM",
                    "place": "Test City",
                }
            ]
        })  # type: ignore[return-value]


def test_get_mints_parses_items() -> None:
    service = MintService(MintServiceDummyClient())
    items = service.get_mints(lang="en")
    assert len(items) == 1
    assert items[0].name == "Test Mint"
    assert items[0].code == "TM"
