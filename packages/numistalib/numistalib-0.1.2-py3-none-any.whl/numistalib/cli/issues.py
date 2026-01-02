"""Issues CLI commands."""

import asyncio

import click

from numistalib.cli.theme import CLISettings
from numistalib.config import Settings
from numistalib.models import Issue
from numistalib.services import IssueService

# pyright: reportUnusedFunction = false

COMMENT_MAX_LENGTH = 400


def register_issues_commands(parent: click.Group) -> None:
    """Register issues commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to
    """

    @click.command(name="issues")
    @click.argument("type_id", type=int)
    @click.option("--limit", type=int, default=50, help="Results per page")
    @click.option("--lang", default="en", type=click.Choice(["en", "es", "fr"]), help="Language")
    @click.option("-t", "--table", is_flag=True, help="Render results as a table")
    def issues(type_id: int, limit: int, lang: str, table: bool) -> None:
        """Show issues for a type (panel by default, table with -t/--table)."""
        console = CLISettings.console()
        settings = Settings()
        client = Settings.to_async_client(settings)
        service = IssueService(client)
        model_cls = service.MODEL

        try:
            async def consume_issues() -> list[Issue]:
                """Consume all issues from the paginated service."""
                issues_list: list[Issue] = []
                async for issue in service.get_issues_paginated(type_id=type_id, lang=lang, limit=limit):
                    issues_list.append(issue)
                return issues_list

            issues_list = asyncio.run(consume_issues())

            if not issues_list:
                console.print(f"[warning]No issues found for type {type_id}[/warning]")
                return

            if table:
                output = model_cls.render_table(issues_list, f"Issues for Type {type_id}")
                console.print(output)
            else:
                for issue in issues_list:
                    panel = service._format_panel(issue)
                    console.print(panel)

            console.print(f"\n[success]Found {len(issues_list)} issue{'s' if len(issues_list) != 1 else ''}[/success]")

        except (RuntimeError, OSError, ValueError) as err:
            service.handle_cli_error(err, f"listing issues for type {type_id}", "isu-list")

    parent.add_command(issues, name="issues")
    parent.add_command(issues, name="isu")
