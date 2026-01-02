"""Unit tests for BaseService helper methods to improve coverage.

Covers:
- `BaseService._build_params()`
- `BaseService.last_cache_indicator` default
- `BaseService._format_panel()` with a simple model stub
"""

from typing import Any

from rich.panel import Panel
from rich.text import Text

from numistalib.services.base.service import BaseService

from .conftest import DummyClient


class DummyService(BaseService):
    def to_models(self, items, **kwargs):  # type: ignore[override]
        return items


class DummyModel:
    def as_panel(self, style_overrides: dict[str, Any] | None = None) -> Panel:
        return Panel(Text("hello"), title="Thing")


def test_build_params_excludes_none_and_merges_base() -> None:
    params = DummyService(DummyClient())._build_params({"lang": "en"}, q="dollar", issuer=None, year=2020)
    assert params == {"lang": "en", "q": "dollar", "year": 2020}


def test_last_cache_indicator_defaults_to_miss() -> None:
    service = DummyService(DummyClient())
    assert service.last_cache_indicator == "🌐"


def test_format_panel_enhances_title_with_cache_indicator() -> None:
    service = DummyService(DummyClient())
    panel = service._format_panel(DummyModel())
    assert isinstance(panel, Panel)
    # Title should include the cache miss indicator and original title
    assert panel.title and panel.title.startswith("🌐 ")
