"""Numista prices models.

Pydantic models for Numista price estimates.
"""


from typing import Self

from pydantic import Field, computed_field
from rich.table import Table

from numistalib.models.base import NumistaBaseModel


class Price(NumistaBaseModel):
    """Price estimate for a specific issue and grade.

    Maps to Numista price data.
    """

    issue_id: int = Field(gt=0, description="Issue ID")
    grade: str = Field(max_length=10, description="Grade (g, vg, f, vf, xf, au, unc)")
    currency: str = Field(max_length=3, description="ISO 4217 currency code")
    value: float = Field(ge=0, description="Price estimate")

    @computed_field(description="Formatted price display")
    def formatted_price(self) -> str:
        """Price with currency code."""
        return f"{self.currency} {self.value:.2f}"

    @classmethod
    def render_table(cls, items: list[Self], title: str = "") -> Table:
        """Generate table for price list.
        
        Parameters
        ----------
        items : list[Self]
            List of Price instances
        title : str
            Table title
            
        Returns
        -------
        Table
            Rich table with price information
        """
        table = Table(show_header=True, box=None, pad_edge=False, title=title)
        table.add_column("Issue ID", no_wrap=True)
        table.add_column("Grade", no_wrap=True)
        table.add_column("Currency", no_wrap=True)
        table.add_column("Value", no_wrap=True, justify="right")
        
        for price in items:
            table.add_row(
                str(price.issue_id),
                price.grade,
                price.currency,
                f"{price.value:.2f}"
            )
        
        return table
