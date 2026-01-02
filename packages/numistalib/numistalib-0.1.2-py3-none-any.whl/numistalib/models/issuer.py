"""Numista issuer import model.

Minimal Pydantic model for importing issuers from Numista API listings.
Aligns with the subset of fields required for the coinlib issuer table
(country_code, name_en, code, numista_id).
"""


from typing import Self

from pydantic import Field
from rich.table import Table

from numistalib.models.base import NumistaBaseModel


class Issuer(NumistaBaseModel):
    """Issuing country or territory record from Numista.

    Represents a country, territory, or entity that issues coins,
    banknotes, or exonumia. Supports recurse, hierarchical
    relationships.

    Parameters
    ----------
    code : str
        Slug/short code (primary key, max 100 chars)
    name : str
        Display name (max 255 chars)
    flag : str
        URL to flag image
    wikidata_id : str | None
        Optional Wikidata identifier for cross-reference
    level : int
        Hierarchy level (1=country, 2+=subdivision)
    parent_code : str | None
        Parent issuer code if nested (optional)
    parent_name : str | None
        Parent issuer name if nested (optional)
    raw : dict
        Original API payload

    Raises
    ------
    ValidationError
        If required fields missing or invalid types

    Examples
    --------
    >>> issuer = Issuer(
    ...     code="split_notgeld",
    ...     name="Split, City of",
    ...     flag="https://en.numista.com/design/pays/yugoslavia_notgeld.gif",
    ...     wikidata_id="Q1663",
    ...     level=3,
    ...     parent_code="yugoslavia_notgeld",
    ...     parent_name="Yugoslavia Notgeld",
    ...     raw={}
    ... )
    >>> print(f"{issuer.name} (level {issuer.level})")
    Split, City of (level 3)
    """

    code: str = Field(max_length=100, description="Slug/short code (primary key)")
    name: str = Field(max_length=255, description="Display name")
    flag: str | None = Field(None, description="URL to flag image")
    wikidata_id: str | None = Field(None, description="Wikidata identifier for cross-reference")
    level: int | None = Field(None, ge=1, description="Hierarchy level (1=country, 2+=subdivision)")
    parent_code: str | None = Field(None, max_length=100, description="Parent issuer code if nested")
    parent_name: str | None = Field(None, max_length=255, description="Parent issuer name if nested")

    @classmethod
    def render_table(cls, items: list[Self], title: str = "") -> Table:
        """Generate table for issuer list.

        Parameters
        ----------
        items : list[Self]
            List of Issuer instances
        title : str
            Table title

        Returns
        -------
        Table
            Rich table with issuer information
        """
        table = Table(show_header=True, box=None, pad_edge=False, title=title)
        table.add_column("Code", no_wrap=True)
        table.add_column("Name", no_wrap=False)
        table.add_column("Level", no_wrap=True, justify="right")
        table.add_column("Parent", no_wrap=False)
        table.add_column("Wikidata", no_wrap=True)

        for issuer in items:
            table.add_row(
                issuer.code,
                issuer.name,
                str(issuer.level) if issuer.level else "",
                issuer.parent_name or "",
                issuer.wikidata_id or ""
            )

        return table

    def to_dict(self) -> dict[str, object]:
        """Return a compact dict representation for Issuer used by tests."""
        return {
            "code": self.code,
            "name": self.name,
            "level": self.level,
        }
