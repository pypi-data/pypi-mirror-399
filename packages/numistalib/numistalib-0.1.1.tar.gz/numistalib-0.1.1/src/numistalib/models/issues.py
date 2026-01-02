"""Numista issues models.

Pydantic models for Numista coin issues (specific years/mints of a type).
"""

from datetime import date, datetime
from typing import Any, Self

from pydantic import Field, HttpUrl, computed_field, field_validator
from rich.table import Table

from numistalib.models.base import NumistaBaseModel
from numistalib.models.references import Reference


class Mark(NumistaBaseModel):
    """Mint mark, privy mark, or die mark on a coin.

    Parameters
    ----------
    mark_id : int
        Unique ID of the mark
    title : str | None
        Title/name of the mark (optional)
    picture : HttpUrl | None
        URL to picture of the mark (optional)
    letters : str | None
        Letters of the mark (optional)

    Notes
    -----
    Marks either have a picture or letters, not both.
    """

    mark_id: int = Field(description="Mark ID")
    title: str | None = Field(None, description="Mark title")
    picture: HttpUrl | None = Field(None, description="URL to mark picture")
    letters: str | None = Field(None, description="Mark letters")


class Signature(NumistaBaseModel):
    """Signature on a banknote.

    Parameters
    ----------
    signer_name : str
        Name of the person who signed
    signer_title : str | None
        Job title of the person who signed (optional)
    """

    signer_name: str = Field(description="Signer name")
    signer_title: str | None = Field(None, description="Signer job title")


class Issue(NumistaBaseModel):
    """Coin issue (specific year/mint of a type).

    Maps to Numista issue entity. Issues represent specific mintings
    of a type with particular year, mint mark, or variety.

    Parameters
    ----------
    numista_id : int
        Numista issue ID (unique identifier)
    type_id : int
        Parent type ID
    is_dated : bool
        Whether issue has a visible date on the coin
    year : int | None
        Year visible on coin (optional)
    gregorian_year : int | None
        Gregorian calendar year (optional)
    mint_letter : str | None
        Mint mark or letter (max 10 chars, optional)
    mintage : int | None
        Number of coins minted (optional)
    comment : str | None
        Additional notes or variety information (optional)
    raw : dict
        Original API payload

    Raises
    ------
    ValidationError
        If required fields missing or invalid types

    Examples
    --------
    >>> issue = Issue(
    ...     numista_id=123456,
    ...     type_id=95420,
    ...     is_dated=True,
    ...     year=1622,
    ...     gregorian_year=1622,
    ...     mint_letter="D",
    ...     mintage=50000,
    ...     raw={}
    ... )
    >>> print(f"{issue.year} {issue.mint_letter}")
    1622 D
    """

    numista_id: int = Field(description="Numista issue ID")
    type_id: int = Field(description="Parent type ID")
    is_dated: bool = Field(description="Whether issue has a visible date")
    year: int | None = Field(None, description="Year visible on coin")
    gregorian_year: int | None = Field(None, description="Gregorian calendar year")
    min_year: int | None = Field(None, description="First year of issuance (non-dated)")
    max_year: int | None = Field(None, description="Last year of issuance (non-dated)")
    mint_letter: str | None = Field(None, max_length=10, description="Mint mark")
    marks: list[Mark] = Field(default_factory=list, description="Mint/privy/die marks")
    signatures: list[Signature] = Field(default_factory=list, description="Signatures (banknotes)")
    mintage: int | None = Field(None, description="Number minted")
    references: list[Reference] = Field(default_factory=list, description="Catalogue references")
    comment: str | None = Field(None, description="Additional notes")

    @classmethod
    def render_table(cls, items: list[Self], title: str = "") -> Table:
        """Generate table for issue list.

        Parameters
        ----------
        items : list[Self]
            List of Issue instances
        title : str
            Table title

        Returns
        -------
        Table
            Rich table with issue information
        """
        table = Table(show_header=True, box=None, pad_edge=False, title=title)
        table.add_column("ID", no_wrap=True)
        table.add_column("Type ID", no_wrap=True)
        table.add_column("Year", no_wrap=True)
        table.add_column("Mint", no_wrap=True)
        table.add_column("Mintage", no_wrap=True, justify="right")
        table.add_column("Comment", no_wrap=False)

        for issue in items:
            # Display year or year range
            year_display = ""
            if issue.year:
                year_display = str(issue.year)
            elif issue.min_year and issue.max_year:
                year_display = f"{issue.min_year}-{issue.max_year}"
            elif issue.min_year:
                year_display = f"{issue.min_year}+"

            table.add_row(
                str(issue.numista_id),
                str(issue.type_id),
                year_display,
                issue.mint_letter or "",
                f"{issue.mintage:,}" if issue.mintage else "",
                issue.comment or ""
            )

        return table


class IssueTerms(NumistaBaseModel):
    """Terms related to a coin issue.

    Parameters
    ----------
    is_issued : bool
        Whether the issue was officially issued
    issue_date : date | None
        Official issue date (optional)

    Raises
    ------
    ValidationError
        If required fields missing or invalid types

    Examples
    --------
    >>> terms = IssueTerms(
    ...     is_issued=True,
    ...     issue_date=date(1973, 1, 1)
    ... )
    >>> print(terms.is_issued)
    True
    """

    is_issued: bool = Field(description="Whether the issue was officially issued")
    issue_date: date | None = Field(None, description="Official issue date")

    @field_validator("issue_date", mode="before")
    @classmethod
    def parse_partial_date(cls, v: Any) -> date | None:
        """Handle partial dates with 00 day or month and various formats."""
        if v is None:
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            # Skip partial dates with 00
            if "00" in v or v.endswith("-00"):
                return None
            # Try multiple date formats
            formats = [
                "%Y-%m-%d",      # 1988-02-15
                "%Y/%m/%d",      # 1988/02/15
                "%d-%m-%Y",      # 15-02-1988
                "%d/%m/%Y",      # 15/02/1988
                "%m-%d-%Y",      # 02-15-1988
                "%m/%d/%Y",      # 02/15/1988
                "%Y",            # 1988 (year only)
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    continue
            return None
        return None


class IssuingEntity(NumistaBaseModel):
    """Entity responsible for issuing a coin.

    Parameters
    ----------
    id : int
        Unique identifier for the issuing entity
    name : str
        Name of the issuing entity
    wikidata_id : str | None
        Optional Wikidata identifier
    """

    id: int = Field(alias="numista_id", description="Unique identifier for the issuing entity")
    name: str = Field(description="Name of the issuing entity")
    wikidata_id: str | None = Field(None, description="Wikidata identifier")

    @computed_field
    def wikidata_url(self) -> HttpUrl | None:
        """Computed Wikidata URL from `wikidata_id`.

        Returns
        -------
        HttpUrl | None
            Full Wikidata URL if `wikidata_id` present, else None.
        """
        if self.wikidata_id:
            return HttpUrl(f"https://www.wikidata.org/wiki/{self.wikidata_id}")
        return None
