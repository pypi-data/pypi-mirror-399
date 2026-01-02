"""Unit tests for IssuerService happy path with mocked client.

Covers get_issuers conversion and logging path without network calls.
"""

from typing import Any

from numistalib.client import NumistaResponse
from numistalib.services.issuer.service import IssuerService

from .conftest import DummyClient, DummyResponse


class IssuerServiceDummyClient(DummyClient):
    def get(self, url: str, **kwargs: Any) -> NumistaResponse:  # type: ignore[override]
        assert url == "/issuers"
        return DummyResponse({
            "issuers": [
                {
                    "code": "us",
                    "name": "United States",
                    "wikidata_id": "Q30",
                }
            ]
        })  # type: ignore[return-value]


def test_get_issuers_parses_items() -> None:
    service = IssuerService(IssuerServiceDummyClient())
    items = service.get_issuers(lang="en")
    assert len(items) == 1
    assert items[0].code == "us"
    assert items[0].name == "United States"
