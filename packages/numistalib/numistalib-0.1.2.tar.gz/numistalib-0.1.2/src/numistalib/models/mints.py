"""Numista mints models.

Pydantic models for Numista mint facilities.
"""

from typing import Self

from pydantic import Field, computed_field
from rich.table import Table

from numistalib.models.base import NumistaBaseModel
from numistalib.models.issuer import Issuer

# Constant for mints still in operation
MINT_ACTIVE_END_YEAR = 9999


class Mint(NumistaBaseModel):
    """Mint facility information.

    Maps to Numista mint entity.

    Parameters
    ----------
    id : int
        Numista mint ID
    name : str
        Mint name in chosen language
    local_name : str | None
        Mint name in local language (optional)
    code : str | None
        Mint code or abbreviation (optional)
    place : str | None
        Place where mint is located (optional)
    country : Issuer | None
        Country issuer information (optional)
    start_year : int | None
        First year of operation (optional)
    end_year : int | None
        Last year of operation, 9999=still active (optional)
    nomisma_id : str | None
        Nomisma identifier (optional)
    wikidata_id : str | None
        Wikidata identifier (optional)
    country_code : str | None
        Issuing country code - deprecated, use country.code (optional)
    """

    id: int = Field(alias="numista_id", gt=0, description="Numista ID")
    name: str = Field(max_length=255, description="Mint facility name")
    local_name: str | None = Field(None, max_length=255, description="Mint name in local language")
    code: str | None = Field(None, max_length=50, description="Mint code or abbreviation")
    place: str | None = Field(None, max_length=255, description="Place where mint is located")
    country: Issuer | None = Field(None, description="Country issuer information")
    start_year: int | None = Field(None, description="First year of operation")
    end_year: int | None = Field(None, description="Last year of operation (9999=still active)")
    nomisma_id: str | None = Field(None, max_length=100, description="Nomisma identifier")
    wikidata_id: str | None = Field(None, max_length=100, description="Wikidata identifier")
    country_code: str | None = Field(None, max_length=50, description="Issuing country code (deprecated)")

    @computed_field(description="Formatted mint identifier")
    def mint_identifier(self) -> str:
        """Mint code if available, otherwise name."""
        return self.code if self.code else self.name

    def render_compact(self) -> str:
        """Render compact mint display."""
        lines = [f"[bold]{self.name}[/bold]"]
        if self.local_name and self.local_name != self.name:
            lines.append(f"Local: {self.local_name}")
        if self.code:
            lines.append(f"Code: {self.code}")
        if self.place:
            lines.append(f"Place: {self.place}")
        if self.country:
            lines.append(f"Country: {self.country.name}")
        elif self.country_code:
            lines.append(f"[dim]{self.country_code}[/dim]")
        if self.start_year or self.end_year:
            years = f"Active: {self.start_year or '?'}-"
            years += "present" if self.end_year == MINT_ACTIVE_END_YEAR else (str(self.end_year) if self.end_year else "?")
            lines.append(years)
        return "\n".join(lines)

    @classmethod
    def render_table(cls, items: list[Self], title: str = "") -> Table:
        """Generate table for mint list.

        Parameters
        ----------
        items : list[Self]
            List of Mint instances
        title : str
            Table title

        Returns
        -------
        Table
            Rich table with mint information
        """
        table = Table(show_header=True, box=None, pad_edge=False, title=title)
        table.add_column("Id", no_wrap=True)
        table.add_column("Name", no_wrap=True)
        table.add_column("Code", no_wrap=True)
        table.add_column("Place", no_wrap=True)
        table.add_column("Country", no_wrap=True)
        table.add_column("Years", no_wrap=True)

        for mint in items:
            years = ""
            if mint.start_year and mint.end_year:
                end = "present" if mint.end_year == MINT_ACTIVE_END_YEAR else str(mint.end_year)
                years = f"{mint.start_year}-{end}"
            elif mint.start_year:
                years = f"{mint.start_year}+"

            table.add_row(
                str(mint.id),
                mint.name,
                mint.code or "",
                mint.place or "",
                mint.country.name if mint.country else (mint.country_code or ""),
                years
            )

        return table
