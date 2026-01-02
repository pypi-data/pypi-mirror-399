"""Integration tests for Prices CLI commands (READ operations).

Tests:
- prices (get prices for a type/issue)
"""

import pytest
from click.testing import CliRunner


class TestPrices:
    """Integration tests for 'prices' command."""

    def test_get_prices(self, cli_runner: CliRunner, cli, api_key: str, known_type_id: int, known_issue_id: int) -> None:
        """Test getting prices for type and issue."""
        result = cli_runner.invoke(
            cli,
            ["prices", str(known_type_id), str(known_issue_id)],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"

    def test_get_prices_with_currency(
        self,
        cli_runner: CliRunner,
        cli,
        api_key: str,
        known_type_id: int,
        known_issue_id: int,
    ) -> None:
        """Test getting prices with currency parameter."""
        result = cli_runner.invoke(
            cli,
            [
                "prices",
                str(known_type_id),
                str(known_issue_id),
                "--currency",
                "USD",
            ],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"

    def test_get_prices_with_language(
        self,
        cli_runner: CliRunner,
        cli,
        api_key: str,
        known_type_id: int,
        known_issue_id: int,
    ) -> None:
        """Test getting prices with language parameter."""
        result = cli_runner.invoke(
            cli,
            ["prices", str(known_type_id), str(known_issue_id), "--lang", "fr"],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"
