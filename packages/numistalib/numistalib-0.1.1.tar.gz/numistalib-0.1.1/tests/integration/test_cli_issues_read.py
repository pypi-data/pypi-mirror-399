"""Integration tests for Issues CLI commands (READ operations).

Tests:
- issues (get issues for a type)
"""

import pytest
from click.testing import CliRunner


class TestIssues:
    """Integration tests for 'issues' command."""

    def test_get_issues_for_type(self, cli_runner: CliRunner, cli, api_key: str, known_type_id: int) -> None:
        """Test getting issues for a type."""
        result = cli_runner.invoke(
            cli,
            ["issues", str(known_type_id)],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"

    def test_get_issues_with_language(self, cli_runner: CliRunner, cli, api_key: str, known_type_id: int) -> None:
        """Test getting issues with language parameter."""
        result = cli_runner.invoke(
            cli,
            ["issues", str(known_type_id), "--lang", "es"],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"

    def test_get_issues_invalid_type_id(self, cli_runner: CliRunner, cli, api_key: str) -> None:
        """Test getting issues for invalid type ID."""
        result = cli_runner.invoke(
            cli,
            ["issues", "999999999"],
            env={"NUMISTA_API_KEY": api_key},
        )
        # Should fail gracefully
        assert result.exit_code != 0 or "not found" in result.output.lower() or "error" in result.output.lower()
