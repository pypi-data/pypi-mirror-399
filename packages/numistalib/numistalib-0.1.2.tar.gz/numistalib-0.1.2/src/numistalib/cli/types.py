"""Types CLI commands."""

import asyncio
from typing import Any

import click
from rich.table import Table

from numistalib.cli.theme import CLISettings
from numistalib.config import Settings
from numistalib.models import TypeBasic
from numistalib.services import TypeBasicService, TypeFullService

# pyright: reportOptionalMemberAccess = false
# pyright: reportUnusedFunction = false


async def _consume_type_search_results(
    service: TypeBasicService,
    table: Table,
    search_params: dict[str, Any],
) -> int:
    """Consume and display paginated type search results asynchronously.

    Parameters
    ----------
    service : TypeBasicService
        The type service instance
    table : Table
        Rich table to add rows to
    search_params : dict[str, Any]
        Search parameters (query, issuer, year, category, limit)

    Returns
    -------
    int
        Total count of results
    """
    count = 0
    async for result in service.search_types_paginated(**search_params):
        count += 1
        CLISettings.add_model_row(  # Updated to use the refactored method
            table,
            result,
            cache_indicator=service.last_cache_indicator,
        )
    return count


def register_types_commands(parent: click.Group) -> None:
    """Register types commands with parent group."""

    @parent.group()
    def types() -> None:
        """Search and retrieve coin/banknote/exonumia types."""

    @types.command(name="search")
    @click.option("-q", "--query", help="Full-text search query")
    @click.option("-i", "--issuer", help="Issuer code (e.g., 'united-states')")
    @click.option("-y", "--year", type=int, help="Filter by year")
    @click.option("-c", "--category", type=click.Choice(["coin", "banknote", "exonumia"]), help="Category")
    @click.option("--limit", type=int, default=50, help="Maximum total results")
    @click.option("--lang", default="en", type=click.Choice(["en", "es", "fr"]), help="Language")
    def types_search(
        query: str | None,
        issuer: str | None,
        year: int | None,
        category: str | None,
        limit: int,
        lang: str,
    ) -> None:
        """Search the catalogue for types."""
        console = CLISettings.console()
        settings = Settings()
        client = Settings.to_async_client(settings)
        service = TypeBasicService(client)

        try:
            # settings already created above

            # Use model-driven table rendering for concise headers and values

            search_params: dict[str, Any] = {
                "query": query,
                "issuer": issuer,
                "year": year,
                "category": category,
                "limit": limit,
                "lang": lang,
            }

            # Collect items via async pagination to pass to model's renderer
            collected: list[TypeBasic] = []

            async def _collect() -> None:
                async for result in service.search_types_paginated(**search_params):
                    collected.append(result)
            asyncio.run(_collect())

            # Render table using model's classmethod
            output_table = TypeBasic.render_list(collected)
            console.print(output_table)
            result_count = len(collected)

            if result_count == 0:
                console.print("[warning]No results found[/warning]")
            else:
                suffix = f" for '{query}'" if query else ""
                console.print(f"\n[success]Displayed {result_count} result{'s' if result_count != 1 else ''}{suffix}[/success]")

        except Exception as err:  # noqa: BLE001
            service.handle_cli_error(err, "searching types", "types-search")

    @types.command(name="get")
    @click.argument("type_id", type=int)
    @click.option("--lang", default="en", type=click.Choice(["en", "es", "fr"]), help="Language")
    def types_get(type_id: int, lang: str) -> None:
        """Retrieve full details for a specific type by ID."""
        CLISettings.console()
        settings = Settings()
        client = Settings.to_client(settings)
        service = TypeFullService(client)

        try:
            result = service.get_type(type_id, lang=lang)
            console = CLISettings.console()
            for panel in result.render_detail(service.last_cache_indicator):
                console.print(panel)
            console.print(CLISettings.LICENSE_TEXT, style="footer")
        except Exception as err:  # noqa: BLE001
            service.handle_cli_error(err, f"retrieving type {type_id}", "types-get")
