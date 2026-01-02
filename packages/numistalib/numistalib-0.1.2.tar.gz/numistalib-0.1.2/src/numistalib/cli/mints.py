"""Mints CLI commands."""


import click

from numistalib.cli.theme import CLISettings
from numistalib.config import Settings
from numistalib.services import MintService

# pyright: reportUnusedFunction = false


def register_mints_commands(parent: click.Group) -> None:
    """Register mints commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to
    """

    @parent.command()
    @click.option("--lang", default="en", type=click.Choice(["en", "es", "fr"]), help="Language")
    def mints(lang: str) -> None:
        """List all mints.

        Examples:
            numistalib mints
            numistalib mints --lang es
        """
        settings = Settings()
        client = Settings.to_client(settings)
        service = MintService(client)
        model_cls = getattr(service, "MODEL", None)

        try:
            results = service.get_mints(lang=lang)

            if not results:
                CLISettings.console().print("[warning]No mints found[/warning]")
                return

            output = model_cls.render_table(results, "Mints")  # type: ignore[union-attr]
            CLISettings.console().print(output)
            CLISettings.console().print(f"\n[success]Found {len(results)} mints[/success]")

        except (RuntimeError, OSError, ValueError) as err:
            service.handle_cli_error(err, "listing mints", "mints-list")

    @parent.command(name="mint")
    @click.argument("mint_id", type=int)
    @click.option("--lang", default="en", type=click.Choice(["en", "es", "fr"]), help="Language")
    def mint(mint_id: int, lang: str) -> None:
        """Show details for a specific mint."""
        console = CLISettings.console()
        settings = Settings()
        client = Settings.to_client(settings)
        service = MintService(client)

        try:
            result = service.get_mint(mint_id, lang=lang)

            panel = service._format_panel(result)
            console.print(panel)
            console.print("\n[success]Displayed mint details[/success]")

        except (RuntimeError, OSError, ValueError) as err:
            service.handle_cli_error(err, f"retrieving mint {mint_id}", "mint-get")

    # Alias for convenience
    parent.add_command(mint, name="mnt")
