"""Numista update models.

Pydantic models for Numista API write operations (POST/PATCH).
"""


from pydantic import Field

from numistalib.models.base import NumistaBaseModel


class TypeUpdate(NumistaBaseModel):
    """Type creation/update payload.

    Maps to Numista type_update schema for POST/PATCH operations.

    Parameters
    ----------
    title : str
        Type title (max 500 chars)
    category : str
        Category: coin, banknote, or exonumia
    issuer_code : str | None
        Issuer code (optional)
    value_text : str | None
        Face value as text (optional)
    value_numeric : float | None
        Numeric face value (optional)
    currency_code : str | None
        ISO 4217 currency code (optional)
    composition : str | None
        Metal composition (optional)
    weight : float | None
        Weight in grams (optional)
    diameter : float | None
        Diameter in mm (optional)
    thickness : float | None
        Thickness in mm (optional)
    obverse_description : str | None
        Obverse description (optional)
    obverse_lettering : str | None
        Obverse lettering (optional)
    reverse_description : str | None
        Reverse description (optional)
    reverse_lettering : str | None
        Reverse lettering (optional)

    Examples
    --------
    >>> update = TypeUpdate(
    ...     title="1 Dollar",
    ...     category="coin",
    ...     issuer_code="usa",
    ...     composition="Silver",
    ...     weight=26.73
    ... )
    >>> print(update.title)
    1 Dollar
    """

    title: str = Field(max_length=500, description="Type title")
    category: str = Field(max_length=50, description="Category")
    issuer_code: str | None = Field(None, max_length=100, description="Issuer code")
    value_text: str | None = Field(None, max_length=100, description="Face value text")
    value_numeric: float | None = Field(None, description="Numeric face value")
    currency_code: str | None = Field(None, max_length=10, description="Currency code")
    composition: str | None = Field(None, max_length=500, description="Composition")
    weight: float | None = Field(None, description="Weight in grams")
    diameter: float | None = Field(None, description="Diameter in mm")
    thickness: float | None = Field(None, description="Thickness in mm")
    obverse_description: str | None = Field(None, description="Obverse description")
    obverse_lettering: str | None = Field(None, description="Obverse lettering")
    reverse_description: str | None = Field(None, description="Reverse description")
    reverse_lettering: str | None = Field(None, description="Reverse lettering")

    def to_dict(self) -> dict[str, object]:
        """Convert update to dictionary representation.

        Returns
        -------
        dict[str, object]
            Dictionary representation excluding None values
        """
        return {k: v for k, v in self.model_dump().items() if v is not None}


class IssueUpdate(NumistaBaseModel):
    """Issue creation/update payload.

    Maps to Numista issue_update schema for POST/PATCH operations.

    Parameters
    ----------
    is_dated : bool
        Whether issue has a visible date
    year : int | None
        Year visible on coin (optional)
    gregorian_year : int | None
        Gregorian calendar year (optional)
    mint_letter : str | None
        Mint mark (optional)
    mintage : int | None
        Number minted (optional)
    comment : str | None
        Additional notes (optional)

    Examples
    --------
    >>> update = IssueUpdate(
    ...     is_dated=True,
    ...     year=2024,
    ...     gregorian_year=2024,
    ...     mint_letter="P",
    ...     mintage=1000000
    ... )
    >>> print(f"{update.year} {update.mint_letter}")
    2024 P
    """

    is_dated: bool = Field(description="Whether issue has visible date")
    year: int | None = Field(None, description="Year visible on coin")
    gregorian_year: int | None = Field(None, description="Gregorian calendar year")
    mint_letter: str | None = Field(None, max_length=10, description="Mint mark")
    mintage: int | None = Field(None, description="Number minted")
    comment: str | None = Field(None, description="Additional notes")

    def to_dict(self) -> dict[str, object]:
        """Convert update to dictionary representation.

        Returns
        -------
        dict[str, object]
            Dictionary representation excluding None values
        """
        return {k: v for k, v in self.model_dump().items() if v is not None}


class TypeSideUpdate(NumistaBaseModel):
    """Type side (obverse/reverse) update payload.

    Maps to Numista type_side_update schema for editing coin sides.

    Parameters
    ----------
    engravers : list[str] | None
        List of engraver names (optional)
    description : str | None
        Side description (optional)
    lettering : str | None
        Side lettering/inscription (optional)

    Examples
    --------
    >>> side = TypeSideUpdate(
    ...     engravers=["John Doe", "Jane Smith"],
    ...     description="National emblem",
    ...     lettering="E PLURIBUS UNUM"
    ... )
    >>> print(side.engravers)
    ['John Doe', 'Jane Smith']
    """

    engravers: list[str] | None = Field(None, description="List of engraver names")
    description: str | None = Field(None, description="Side description")
    lettering: str | None = Field(None, description="Side lettering")

    def to_dict(self) -> dict[str, object]:
        """Convert update to dictionary representation.

        Returns
        -------
        dict[str, object]
            Dictionary representation excluding None values
        """
        return {k: v for k, v in self.model_dump().items() if v is not None}

    @property
    def panel_template(self) -> str:
        """Return formatted panel content for type side update display."""
        engravers_str = ", ".join(self.engravers) if self.engravers else ""
        return f"""Engravers: {engravers_str}
Description: {self.description or ""}
Lettering: {self.lettering or ""}"""


__all__ = [
    "IssueUpdate",
    "TypeSideUpdate",
    "TypeUpdate",
]
