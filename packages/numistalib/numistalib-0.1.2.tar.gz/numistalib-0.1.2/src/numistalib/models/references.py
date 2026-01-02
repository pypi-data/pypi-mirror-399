"""Numista reference and localized label models.

Pydantic models for reference catalogues and multilingual labels.
"""


from typing import Any, Self

from pydantic import Field, HttpUrl, computed_field, model_validator
from rich.table import Table

from numistalib.models.base import NumistaBaseModel


class Catalogue(NumistaBaseModel):
    """Catalogue information.

    Parameters
    ----------
    id : int
        Numista catalogue ID
    code : str
        Catalogue code identifier
    """
    id: int = Field(description="Numista catalogue ID")
    code: str = Field(max_length=50, description="Catalogue code")


class Reference(NumistaBaseModel):
    """Reference catalogue information.

    Parameters
    ----------
    catalogue : Catalogue
        Catalogue details with ID and code
    number : str
        Reference number in catalogue
    url : HttpUrl | None
        External URL to reference (optional)
    """
    catalogue: Catalogue = Field(description="Catalogue information")
    number: str = Field(max_length=100, description="Catalogue reference number")
    url: HttpUrl | None = Field(None, description="External URL to reference")

    @model_validator(mode="before")
    @classmethod
    def handle_catalogue_formats(cls, data: Any) -> Any:
        """Handle both string and object formats for catalogue field.

        API inconsistency: Some endpoints return catalogue as string (code only),
        others return nested object with id and code. This validator normalizes both.
        """
        if isinstance(data, dict) and "catalogue" in data:
            cat = data["catalogue"]
            # If catalogue is a string, convert to Catalogue object with placeholder ID
            if isinstance(cat, str):
                data["catalogue"] = {"id": 0, "code": cat}
        return data

    @computed_field(description="Formatted reference display")
    def display_reference(self) -> str:
        """Formatted catalogue reference."""
        return f"{self.catalogue.code} {self.number}"

    def render_compact(self) -> str:
        """Render compact reference display."""
        ref_text = f"[bold]{self.catalogue.code}[/bold] #{self.number}"
        if self.url:
            return f"[link={self.url}]{ref_text}[/link]"
        return ref_text

    @classmethod
    def render_table(cls, items: list[Self], title: str = "") -> Table:
        """Generate table for reference list with proper None handling.

        Parameters
        ----------
        items : list[Self]
            List of Reference instances
        title : str
            Table title

        Returns
        -------
        Table
            Rich table with catalogue, number, and URL columns
        """
        table = Table(show_header=True, box=None, pad_edge=False, title=title)
        table.add_column("Catalogue", no_wrap=True)
        table.add_column("ID", no_wrap=True, justify="right")
        table.add_column("Number", no_wrap=True)
        table.add_column("Url", no_wrap=False)

        for ref in items:
            table.add_row(
                ref.catalogue.code,
                str(ref.catalogue.id),
                ref.number,
                str(ref.url) if ref.url else ""
            )

        return table


class LocalizedLabel(NumistaBaseModel):
    """Localized text label.

    Maps to Numista localized_label schema for multilingual content.

    Parameters
    ----------
    language : str
        ISO 639-1 language code (2 chars)
    label : str
        Localized text content (max 500 chars)

    Examples
    --------
    >>> label_en = LocalizedLabel(language="en", label="United States")
    >>> label_es = LocalizedLabel(language="es", label="Estados Unidos")
    >>> print(f"{label_en.language}: {label_en.label}")
    en: United States
    """

    language: str = Field(max_length=2, description="ISO 639-1 language code")
    label: str = Field(max_length=500, description="Localized text content")
