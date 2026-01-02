"""Literature CLI commands."""

import click

from numistalib.cli.theme import CLISettings

# pyright: reportUnusedFunction = false

def register_literature_commands(parent: click.Group) -> None:
    """Register literature commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to
    """

    @parent.group()
    def literature() -> None:
        """Access numismatic literature catalogue."""
        pass

    @literature.command(name="get")
    @click.argument("publication_id", type=int)
    def literature_get(publication_id: int) -> None:
        """Get details about a publication.

        Examples:
            numistalib literature get 12345
        """
        CLISettings.console()
        CLISettings.console().print("[warning]Literature commands not yet implemented[/warning]")

    @literature.command(name="search")
    @click.option("-q", "--query", required=True, help="Search query")
    def literature_search(_query: str) -> None:
        """Search literature catalogue.

        Examples:
            numistalib literature search -q "Krause"
        """
        CLISettings.console()
        CLISettings.console().print("[warning]Literature commands not yet implemented[/warning]")
