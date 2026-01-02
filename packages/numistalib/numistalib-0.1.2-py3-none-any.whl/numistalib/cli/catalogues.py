"""Catalogues CLI commands."""


import click

from numistalib.cli.theme import CLISettings
from numistalib.config import Settings
from numistalib.services import CatalogueService

# pyright: reportUnusedFunction = false


def register_catalogues_commands(parent: click.Group) -> None:
    """Register catalogues commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to
    """

    @click.command(name="catalogues")
    @click.option("-t", "--table", is_flag=True, help="Render results as a table")
    def catalogues_cmd(table: bool) -> None:
        """List all reference catalogues (panel default, table with -t/--table)."""
        console = CLISettings.console()
        settings = Settings()
        client = Settings.to_client(settings)
        service = CatalogueService(client)
        model_cls = service.MODEL

        try:
            results = service.get_catalogues()

            if not results:
                console.print("[warning]No catalogues found[/warning]")
                return

            if table:
                output = model_cls.render_table(results, "Reference Catalogues")
                console.print(output)
                console.print(f"\n[success]Found {len(results)} catalogues[/success]")
                return

            # Panel-style rendering using model's as_panel() method
            for catalogue in results:
                panel = service._format_panel(catalogue)
                console.print(panel)

            console.print(
                f"\n[success]Displayed {len(results)} catalogue{'s' if len(results) != 1 else ''}[/success]"
            )

        except (RuntimeError, OSError, ValueError) as err:
            service.handle_cli_error(err, "listing catalogues", "cat-list")

    # Register both names
    parent.add_command(catalogues_cmd, name="catalogues")
    parent.add_command(catalogues_cmd, name="cat")
