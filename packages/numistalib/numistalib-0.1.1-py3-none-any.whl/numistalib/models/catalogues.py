"""Numista catalogues models.

Pydantic models for Numista reference catalogues.
"""


from typing import Self

from pydantic import Field, computed_field
from rich.table import Table

from numistalib.models.base import NumistaBaseModel


class Catalogue(NumistaBaseModel):
    """Reference catalogue information.

    Maps to Numista catalogue entity (e.g., KM, Krause).
    """

    numista_id: int = Field(alias="id", gt=0, description="Numista catalogue ID")
    code: str = Field(max_length=50, description="Catalogue code (e.g., KM, Sp)")
    title: str = Field(max_length=1000, description="Catalogue title")
    author: str | None = Field(None, max_length=500, description="Catalogue author")
    publisher: str | None = Field(None, max_length=500, description="Catalogue publisher")
    isbn13: str | None = Field(None, description="ISBN-13")

    @computed_field(description="Display label for catalogue")
    def display_label(self) -> str:
        """Formatted label with code and title."""
        return f"{self.code}: {self.title}"

    @classmethod
    def render_table(cls, items: list[Self], title: str = "") -> Table:
        """Generate table for catalogue list.
        
        Parameters
        ----------
        items : list[Self]
            List of Catalogue instances
        title : str
            Table title
            
        Returns
        -------
        Table
            Rich table with catalogue information
        """
        table = Table(show_header=True, box=None, pad_edge=False, title=title)
        table.add_column("ID", no_wrap=True)
        table.add_column("Code", no_wrap=True)
        table.add_column("Title", no_wrap=False)
        table.add_column("Author", no_wrap=False)
        table.add_column("Publisher", no_wrap=False)
        
        for cat in items:
            table.add_row(
                str(cat.numista_id),
                cat.code,
                cat.title,
                cat.author or "",
                cat.publisher or ""
            )
        
        return table

    def to_dict(self) -> dict[str, object]:
        """Return a compact dict representation used by tests.

        Includes only core identifying fields and omits optional metadata.
        """
        return {
            "numista_id": self.numista_id,
            "code": self.code,
            "title": self.title,
        }
