"""Configuration management CLI commands."""

import sys

import click

from numistalib.cli.theme import CLISettings
from numistalib.config import Settings

# pyright: reportUnusedFunction = false


def register_config_commands(parent: click.Group) -> None:
    """Register config commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to
    """

    @parent.group()
    def config() -> None:
        """Manage configuration settings."""
        pass

    @config.command(name="get")
    @click.argument("key")
    def config_get(key: str) -> None:
        """Get a configuration value.

        Examples:
            numistalib config get api_key
            numistalib config get cache_dir
        """
        try:
            console = CLISettings.console()
            settings = Settings()
            value = getattr(settings, key.lower(), None)
            if value is None:
                console.print(f"[danger]Setting '{key}' not found[/danger]")
                sys.exit(1)
            console.print(f"[header]{key}:[/header] {value}")
        except (AttributeError, ValueError, KeyError) as err:
            CLISettings.console().print(f"[danger]Error: {err}[/danger]")
            sys.exit(1)

    @config.command(name="list")
    def config_list() -> None:
        """List all configuration settings."""
        try:
            console = CLISettings.console()
            settings = Settings()
            table = CLISettings.create_table("numistalib Configuration")
            table.add_column("Setting")
            table.add_column("Value")

            for field_name in type(settings).model_fields:
                value = getattr(settings, field_name)
                if field_name == "api_key":
                    value = "***" if value else None
                table.add_row(field_name, str(value) if value is not None else "")

            console.print(table)
        except (AttributeError, ValueError) as err:
            CLISettings.console().print(f"[danger]Error: {err}[/danger]")
            sys.exit(1)
