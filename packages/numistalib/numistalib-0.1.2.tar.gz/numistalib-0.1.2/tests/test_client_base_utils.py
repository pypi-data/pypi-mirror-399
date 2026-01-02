"""Unit tests for lightweight client utilities to improve coverage.

Covers:
- `NumistaClientSync._build_url()` relative vs absolute
- `NumistaClient._wrap_response()` cached indicator
- `NumistaClientSync.database_full_path` directory creation
"""

from pathlib import Path

import httpx

from numistalib.client import NumistaClientSync, NumistaResponse


def test_build_url_relative_and_absolute() -> None:
    client = NumistaClientSync(api_key="test-key")
    assert client._build_url("/types") == "https://api.numista.com/v3/types"
    assert client._build_url("https://example.com/x") == "https://example.com/x"


def test_wrap_response_cached_indicator_true() -> None:
    client = NumistaClientSync(api_key="test-key")
    resp = httpx.Response(
        200,
        request=httpx.Request("GET", "https://api.numista.com/v3/ping"),
        extensions={"hishel_from_cache": True},
    )
    wrapped = client._wrap_response(resp)
    assert isinstance(wrapped, NumistaResponse)
    assert wrapped.cached is True
    assert wrapped.cached_indicator == "💾"


def test_database_full_path_creates_directory(tmp_path: Path) -> None:
    client = NumistaClientSync(api_key="test-key", database_cache_dir=str(tmp_path), database_cache_db="x.db")
    full_path = client.database_full_path
    # Directory should exist and full path should point to db inside it
    assert Path(full_path).parent.exists()
    assert Path(full_path).name == "x.db"
