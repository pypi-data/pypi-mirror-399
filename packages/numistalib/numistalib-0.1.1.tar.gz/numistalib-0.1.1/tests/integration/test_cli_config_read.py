"""Integration tests for Config CLI commands (READ operations).

Tests:
- config get
- config list
"""

import pytest
from click.testing import CliRunner


class TestConfigGet:
    """Integration tests for 'config get' command."""

    def test_get_config_key(self, cli_runner: CliRunner, cli) -> None:
        """Test getting a config value by key."""
        # This doesn't require API key
        result = cli_runner.invoke(
            cli,
            ["config", "get", "api_key"],
        )
        # Should complete without error
        assert result.exit_code == 0 or "not found" in result.output.lower(), f"Command failed: {result.output}"


class TestConfigList:
    """Integration tests for 'config list' command."""

    def test_list_config(self, cli_runner: CliRunner, cli) -> None:
        """Test listing all config values."""
        result = cli_runner.invoke(
            cli,
            ["config", "list"],
        )
        # Should complete without error
        assert result.exit_code == 0, f"Command failed: {result.output}"
