"""Unit test for CatalogueService happy path with a mocked client.

Covers parsing of items and logging path without network calls.
"""

from typing import Any

from numistalib.client import NumistaResponse
from numistalib.services.catalogues.service import CatalogueService

from .conftest import DummyClient, DummyResponse


class CatalogueServiceDummyClient(DummyClient):
    def get(self, url: str, **kwargs: Any) -> NumistaResponse:  # type: ignore[override]
        assert url == "/catalogues"
        return DummyResponse({
            "catalogues": [
                {"id": 1, "code": "KM", "title": "Krause-Mishler", "author": "Test"},
                {"id": 2, "code": "SC", "title": "Standard Catalog", "author": None},
            ]
        })  # type: ignore[return-value]


def test_get_catalogues_parses_items() -> None:
    service = CatalogueService(CatalogueServiceDummyClient())
    items = service.get_catalogues()
    assert len(items) == 2
    assert items[0].code == "KM"
    assert items[1].title == "Standard Catalog"
