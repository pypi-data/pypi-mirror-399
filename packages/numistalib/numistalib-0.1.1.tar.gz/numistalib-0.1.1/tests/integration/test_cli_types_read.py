"""Integration tests for Types CLI commands (READ operations).

Tests:
- types search
- types get
"""

import pytest
from click.testing import CliRunner


class TestTypesSearch:
    """Integration tests for 'types search' command."""

    def test_search_with_query(self, cli_runner: CliRunner, cli, api_key: str) -> None:
        """Test searching types by query string."""
        result = cli_runner.invoke(
            cli,
            ["types", "search", "-q", "dollar"],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "dollar" in result.output.lower() or "Dollar" in result.output

    def test_search_with_issuer(self, cli_runner: CliRunner, cli, api_key: str, known_issuer_code: str) -> None:
        """Test searching types by issuer code."""
        result = cli_runner.invoke(
            cli,
            ["types", "search", "--issuer", known_issuer_code],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"

    def test_search_with_category(self, cli_runner: CliRunner, cli, api_key: str) -> None:
        """Test searching types by category."""
        result = cli_runner.invoke(
            cli,
            ["types", "search", "-q", "euro", "--category", "coin"],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"

    def test_search_with_year(self, cli_runner: CliRunner, cli, api_key: str) -> None:
        """Test searching types by year."""
        result = cli_runner.invoke(
            cli,
            ["types", "search", "-q", "dollar", "--year", "2000"],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"

    def test_search_with_pagination(self, cli_runner: CliRunner, cli, api_key: str) -> None:
        """Test searching types with limit."""
        result = cli_runner.invoke(
            cli,
            ["types", "search", "-q", "cent", "--limit", "10"],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"


class TestTypesGet:
    """Integration tests for 'types get' command."""

    def test_get_by_id(self, cli_runner: CliRunner, cli, api_key: str, known_type_id: int) -> None:
        """Test getting type by ID."""
        result = cli_runner.invoke(
            cli,
            ["types", "get", str(known_type_id)],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"
        # Should contain type details
        assert "Title" in result.output or "title" in result.output.lower()

    def test_get_invalid_id(self, cli_runner: CliRunner, cli, api_key: str) -> None:
        """Test getting type with invalid ID."""
        result = cli_runner.invoke(
            cli,
            ["types", "get", "999999999"],
            env={"NUMISTA_API_KEY": api_key},
        )
        # Should fail gracefully
        assert result.exit_code != 0 or "not found" in result.output.lower() or "error" in result.output.lower()

    def test_get_with_language(self, cli_runner: CliRunner, cli, api_key: str, known_type_id: int) -> None:
        """Test getting type with language parameter."""
        result = cli_runner.invoke(
            cli,
            ["types", "get", str(known_type_id), "--lang", "fr"],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"
