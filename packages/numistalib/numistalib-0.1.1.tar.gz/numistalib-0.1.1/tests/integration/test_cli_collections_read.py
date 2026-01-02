"""Integration tests for Collections CLI commands (READ operations).

Tests:
- collections list
- collections items
"""

import pytest
from click.testing import CliRunner


class TestCollectionsList:
    """Integration tests for 'collections list' command."""

    def test_list_collections(self, cli_runner: CliRunner, cli, api_key: str, known_user_id: int) -> None:
        """Test listing collections for a user (OAuth required)."""
        result = cli_runner.invoke(
            cli,
            ["collections", "list", str(known_user_id)],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"


class TestCollectionsItems:
    """Integration tests for 'collections items' command."""

    def test_list_collection_items(self, cli_runner: CliRunner, cli, api_key: str, known_user_id: int) -> None:
        """Test listing items in a user's collection (OAuth required)."""
        result = cli_runner.invoke(
            cli,
            ["collections", "items", str(known_user_id)],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"
