"""Unit tests for TypeBasicService happy path with mocked client.

Covers conversion and logging path without network calls.
"""

from typing import Any

from numistalib.client import NumistaResponse
from numistalib.services.types.service import SearchParams, TypeBasicService

from .conftest import DummyClient, DummyResponse


class TypeServiceDummyClient(DummyClient):
    def get(self, url: str, **kwargs: Any) -> NumistaResponse:  # type: ignore[override]
        assert url == "/types"
        return DummyResponse({
            "types": [
                {
                    "id": 1,
                    "title": "Test Dollar",
                    "category": "coin",
                    "issuer": {"code": "us", "name": "United States"},
                    "min_year": 2000,
                    "max_year": 2010,
                }
            ]
        })  # type: ignore[return-value]


def test_search_types_happy_path() -> None:
    service = TypeBasicService(TypeServiceDummyClient())
    params = SearchParams(query="dollar", page=1, count=10)
    items = service.search_types(params)
    assert len(items) == 1
    assert items[0].title == "Test Dollar"
    assert items[0].issuer.name == "United States"
