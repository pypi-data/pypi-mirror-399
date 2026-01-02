"""Integration tests for Catalogues CLI commands (READ operations).

Tests:
- catalogues (list all catalogues)
"""

from click.testing import CliRunner


class TestCatalogues:
    """Integration tests for 'catalogues' command."""

    def test_list_catalogues(self, cli_runner: CliRunner, cli, api_key: str) -> None:
        """Test listing all catalogues."""
        result = cli_runner.invoke(
            cli,
            ["catalogues"],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"
        # Should contain catalogue names or IDs
        assert len(result.output) > 0
