"""Integration tests for Users CLI commands (READ operations).

Tests:
- users get
- users search
"""

from click.testing import CliRunner


class TestUsersGet:
    """Integration tests for 'users get' command."""

    def test_get_user_by_id(self, cli_runner: CliRunner, cli, api_key: str, known_user_id: int) -> None:
        """Test getting user by ID (OAuth required)."""
        result = cli_runner.invoke(
            cli,
            ["users", "get", str(known_user_id)],
            env={"NUMISTA_API_KEY": api_key},
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"

    def test_get_user_invalid_id(self, cli_runner: CliRunner, cli, api_key: str) -> None:
        """Test getting user with invalid ID (OAuth warning expected)."""
        result = cli_runner.invoke(
            cli,
            ["users", "get", "999999999"],
            env={"NUMISTA_API_KEY": api_key},
        )
        # OAuth not implemented, expects warning
        assert "oauth" in result.output.lower() or "authentication" in result.output.lower()
