"""Unit tests for IssueService happy path with mocked client.

Covers get_issues conversion and logging path without network calls.
"""

from typing import Any

from numistalib.client import NumistaResponse
from numistalib.services.issues.service import IssueService

from .conftest import DummyClient, DummyResponse


class IssueServiceDummyClient(DummyClient):
    def get(self, url: str, **kwargs: Any) -> NumistaResponse:  # type: ignore[override]
        assert "/types/" in url and "/issues" in url
        return DummyResponse({
            "issues": [
                {
                    "id": 501,
                    "type": {"id": 1, "title": "Test Coin"},
                    "is_dated": True,
                    "min_year": 2000,
                    "max_year": 2010,
                }
            ]
        })  # type: ignore[return-value]


def test_get_issues_parses_items() -> None:
    service = IssueService(IssueServiceDummyClient())
    items = service.get_issues(type_id=1)
    assert len(items) == 1
    assert items[0].numista_id == 501
    assert items[0].is_dated is True
    assert items[0].min_year == 2000
