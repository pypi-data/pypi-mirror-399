"""Command-line interface main entry point for numistalib.

Registers all CLI command groups.
"""

import click

from numistalib.cli.catalogues import register_catalogues_commands
from numistalib.cli.collections import register_collections_commands
from numistalib.cli.config import register_config_commands
from numistalib.cli.image_search import register_image_search_commands
from numistalib.cli.issuers import register_issuers_commands
from numistalib.cli.issues import register_issues_commands
from numistalib.cli.literature import register_literature_commands
from numistalib.cli.mints import register_mints_commands
from numistalib.cli.prices import register_prices_commands
from numistalib.cli.types import register_types_commands
from numistalib.cli.users import register_users_commands


@click.group()
@click.version_option(version="0.1.0", prog_name="numistalib")
def cli() -> None:
    """Numista API wrapper - search and manage numismatic data."""
    pass


def main() -> None:
    """Register all command groups and run CLI."""
    register_config_commands(cli)
    register_types_commands(cli)
    register_catalogues_commands(cli)
    register_issuers_commands(cli)
    register_issues_commands(cli)
    register_mints_commands(cli)
    register_collections_commands(cli)
    register_image_search_commands(cli)
    register_literature_commands(cli)
    register_prices_commands(cli)
    register_users_commands(cli)
    cli()


if __name__ == "__main__":
    main()
