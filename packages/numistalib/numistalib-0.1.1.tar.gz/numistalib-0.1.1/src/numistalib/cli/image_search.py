"""Image search CLI commands."""

import click

from numistalib.cli.theme import CLISettings

# pyright: reportUnusedFunction = false

def register_image_search_commands(parent: click.Group) -> None:
    """Register image search commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to
    """

    @parent.command(name="search-image")
    @click.argument("image_path", type=click.Path(exists=True))
    @click.option("--limit", type=int, default=10, help="Number of results")
    def search_image(_image_path: str, _limit: int) -> None:
        """Search catalogue by image.

        Examples:
            numistalib search-image coin.jpg
            numistalib search-image coin.jpg --limit 20
        """
        CLISettings.console()
        CLISettings.console().print("[warning]Image search not yet implemented[/warning]")
