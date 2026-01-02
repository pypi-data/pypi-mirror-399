"""Integration tests for Issuers CLI commands (READ operations).

Tests:
- issuers (list all issuers)
"""

import pytest
from click.testing import CliRunner


class TestIssuers:
    """Integration tests for 'issuers' command."""

    def test_list_issuers(self, cli_runner: CliRunner, cli, api_key: str) -> None:
        """Test listing all issuers."""
        result = cli_runner.invoke(
            cli,
            ["issuers"],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"
        # Should contain issuer data
        assert len(result.output) > 0

    def test_list_issuers_with_language(self, cli_runner: CliRunner, cli, api_key: str) -> None:
        """Test listing issuers with language parameter."""
        result = cli_runner.invoke(
            cli,
            ["issuers", "--lang", "fr"],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"
