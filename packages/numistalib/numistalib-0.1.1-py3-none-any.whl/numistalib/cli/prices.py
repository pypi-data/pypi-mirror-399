"""Prices CLI commands."""


import click

from numistalib.cli.theme import CLISettings
from numistalib.config import Settings
from numistalib.services import PriceService

# pyright: reportUnusedFunction = false


def register_prices_commands(parent: click.Group) -> None:
    """Register prices commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to
    """

    @parent.command(name="prices")
    @click.argument("type_id", type=int)
    @click.argument("issue_id", type=int)
    @click.option("--currency", type=str, help="Currency code (e.g., USD, EUR)")
    @click.option("--lang", default="en", type=click.Choice(["en", "es", "fr"]), help="Language")
    def prices(type_id: int, issue_id: int, currency: str | None, lang: str) -> None:
        """Get price estimates for an issue.

        Examples:
            numistalib prices 95420 123456
        """
        settings = Settings()
        client = Settings.to_client(settings)
        service = PriceService(client)

        model_cls = service.MODEL

        try:

            prices_list = service.get_prices(type_id=type_id, issue_id=issue_id, currency=currency, lang=lang)

            if not prices_list:
                CLISettings.console().print(f"[warning]No prices found for type {type_id}, issue {issue_id}[/warning]")
                return

            output = model_cls.render_table(prices_list, f"Prices for Type {type_id}, Issue {issue_id}")
            CLISettings.console().print(output)
            CLISettings.console().print(f"\n[success]Found {len(prices_list)} price estimates[/success]")
        except (RuntimeError, OSError, ValueError) as err:
            service.handle_cli_error(err, f"getting prices for type {type_id}, issue {issue_id}", "prices-get")
