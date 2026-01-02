"""Integration tests for Mints CLI commands (READ operations).

Tests:
- mints (list all mints)
- mint (get single mint by ID)
"""

import pytest
from click.testing import CliRunner


class TestMints:
    """Integration tests for 'mints' command."""

    def test_list_mints(self, cli_runner: CliRunner, cli, api_key: str) -> None:
        """Test listing all mints."""
        result = cli_runner.invoke(
            cli,
            ["mints"],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"
        # Should contain mint data
        assert len(result.output) > 0

    def test_list_mints_with_language(self, cli_runner: CliRunner, cli, api_key: str) -> None:
        """Test listing mints with language parameter."""
        result = cli_runner.invoke(
            cli,
            ["mints", "--lang", "es"],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"


class TestMint:
    """Integration tests for 'mint' command."""

    def test_get_mint_by_id(self, cli_runner: CliRunner, cli, api_key: str, known_mint_id: int) -> None:
        """Test getting mint by ID."""
        result = cli_runner.invoke(
            cli,
            ["mint", str(known_mint_id)],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"

    def test_get_mint_with_language(self, cli_runner: CliRunner, cli, api_key: str, known_mint_id: int) -> None:
        """Test getting mint with language parameter."""
        result = cli_runner.invoke(
            cli,
            ["mint", str(known_mint_id), "--lang", "fr"],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"

    def test_get_mint_invalid_id(self, cli_runner: CliRunner, cli, api_key: str) -> None:
        """Test getting mint with invalid ID."""
        result = cli_runner.invoke(
            cli,
            ["mint", "999999999"],
            env={"NUMISTA_API_KEY": api_key},
        )
        # Should fail gracefully
        assert result.exit_code != 0 or "not found" in result.output.lower() or "error" in result.output.lower()
