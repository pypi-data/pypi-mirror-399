"""Issuers CLI commands."""

import asyncio

import click

from numistalib.cli.theme import CLISettings
from numistalib.config import Settings
from numistalib.models import Issuer
from numistalib.services import IssuerService

# pyright: reportUnusedFunction = false


def register_issuers_commands(parent: click.Group) -> None:
    """Register issuers commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to
    """

    @click.command(name="issuers")
    @click.option("--lang", default="en", type=click.Choice(["en", "es", "fr"]), help="Language")
    @click.option("--limit", type=int, default=50, help="Results per page")
    @click.option("-t", "--table", is_flag=True, help="Render results as a table")
    def issuers(lang: str, limit: int, table: bool) -> None:
        """List issuing entities (panel default, table with -t/--table)."""
        console = CLISettings.console()
        settings = Settings()
        client = Settings.to_async_client(settings)
        service = IssuerService(client)
        model_cls = service.MODEL

        try:
            issuers_list: list[Issuer] = []

            async def consume_issuers() -> list[Issuer]:
                """Consume all issuers from the paginated service."""
                async for issuer in service.get_issuers_paginated(lang=lang, limit=limit):
                    issuers_list.append(issuer)
                return issuers_list

            issuers_list = asyncio.run(consume_issuers())

            if not issuers_list:
                console.print("[warning]No issuers found[/warning]")
                return

            if table:
                output = model_cls.render_table(issuers_list, "Issuers")
                console.print(output)
            else:
                for issuer in issuers_list:
                    panel = service._format_panel(issuer)
                    console.print(panel)

            console.print(f"\n[success]Found {len(issuers_list)} issuer{'s' if len(issuers_list) != 1 else ''}[/success]")

        except (RuntimeError, OSError, ValueError) as err:
            service.handle_cli_error(err, "listing issuers", "isr-list")

    parent.add_command(issuers, name="issuers")
    parent.add_command(issuers, name="isr")
