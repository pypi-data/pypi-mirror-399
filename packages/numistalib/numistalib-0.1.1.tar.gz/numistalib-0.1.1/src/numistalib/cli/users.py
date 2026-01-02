"""Users CLI commands."""

import click

from numistalib.cli.theme import CLISettings

# pyright: reportUnusedFunction=false

def register_users_commands(parent: click.Group) -> None:
    """Register users commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to
    """

    @parent.group()
    def users() -> None:
        """Access user information."""
        pass

    @users.command(name="get")
    @click.argument("user_id", type=int)
    def users_get(user_id: int) -> None:
        """Get details about a user.

        Examples:
            numistalib users get 12345
        """
        CLISettings.console().print("[warning]User commands require OAuth authentication (not yet implemented)[/warning]")

    @users.command(name="search")
    @click.option("-q", "--query", required=True, help="Username search query")
    def users_search(query: str) -> None:
        """Search for users.

        Examples:
            numistalib users search -q "john"
        """
        CLISettings.console().print("[warning]User commands not yet implemented[/warning]")
