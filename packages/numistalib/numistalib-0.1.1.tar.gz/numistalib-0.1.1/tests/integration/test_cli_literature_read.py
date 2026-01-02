"""Integration tests for Literature CLI commands (READ operations).

Tests:
- literature get
- literature search
"""

import pytest
from click.testing import CliRunner


class TestLiteratureGet:
    """Integration tests for 'literature get' command."""

    def test_get_publication_by_id(self, cli_runner: CliRunner, cli, api_key: str, known_publication_id: str) -> None:
        """Test getting publication by ID (NO lang parameter per Swagger)."""
        result = cli_runner.invoke(
            cli,
            ["literature", "get", known_publication_id],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"
