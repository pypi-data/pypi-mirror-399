"""Numista literature models.

Pydantic models for Numista numismatic literature catalogue.
"""

from typing import Literal

from pydantic import Field, HttpUrl

from numistalib.models.base import NumistaBaseModel


class Contributor(NumistaBaseModel):
    """Publication contributor information.

    Parameters
    ----------
    role : Literal["author", "editor", "translator"]
        Contributor's role
    name : str
        Full name of the contributor
    id : int | None
        Unique ID of the person in Numista
    """

    role: Literal["author", "editor", "translator"] = Field(description="Contributor's role")
    name: str = Field(description="Full name of the contributor")
    id: int | None = Field(None, description="Unique ID of the person")


class Publisher(NumistaBaseModel):
    """Publisher information.

    Parameters
    ----------
    name : str
        Name of the publisher
    id : int | None
        Unique ID of the publisher in Numista
    """

    name: str = Field(description="Name of the publisher")
    id: int | None = Field(None, description="Unique ID of the publisher")


class PublicationPlace(NumistaBaseModel):
    """Publication place information.

    Parameters
    ----------
    name : str
        City and country of publication
    geonames_id : str | None
        GeoNames ID for location reference
    """

    name: str = Field(description="City and country of publication")
    geonames_id: str | None = Field(None, description="GeoNames ID for location reference")


class PartOf(NumistaBaseModel):
    """Parent publication reference.

    Parameters
    ----------
    type : Literal["volume_group", "volume", "article_group"]
        Type of parent publication
    id : str
        Unique ID of the parent publication
    title : str
        Title of the parent publication
    volume_number : str | None
        Number or specific title the volume has within its volume group
    """

    type: Literal["volume_group", "volume", "article_group"] = Field(description="Type of parent")
    id: str = Field(description="Unique ID of the parent publication")
    title: str = Field(description="Title of the parent publication")
    volume_number: str | None = Field(
        None,
        description="Number or specific title the volume has within its volume group",
    )


class Publication(NumistaBaseModel):
    """Bibliographic publication record.

    Represents a volume (book), article (authored book chapter),
    series of books (volume_group), or series of articles (article_group).

    Parameters
    ----------
    id : str
        Numista publication ID
    type : Literal["volume", "article", "volume_group", "article_group"]
        Type of publication
    title : str
        Publication title
    url : HttpUrl | None
        URL of the publication entry
    translated_title : str | None
        Title translated into English
    volume_number : str | None
        Volume number within group (volumes only)
    subtitle : str | None
        Subtitle (volumes only)
    translated_subtitle : str | None
        Subtitle translated into English (volumes only)
    edition : str | None
        Edition information (volumes only)
    languages : list[str] | None
        ISO 639 (alpha-2) language codes
    year : int | None
        Publication year (for volumes and articles)
    page_count : int | None
        Total number of pages (volumes only)
    pages : str | None
        Page range (articles only)
    cover : Literal["softcover", "hardcover", "spiral", "hidden_spiral"] | None
        Type of cover (volumes only)
    isbn10 : str | None
        ISBN-10 code (volumes only)
    isbn13 : str | None
        ISBN-13 code (volumes only)
    issn : str | None
        ISSN code (volume groups only)
    oclc_number : str | None
        OCLC catalogue number
    contributors : list[Contributor] | None
        List of contributors (authors, editors, translators)
    publishers : list[Publisher] | None
        Information about the publishers (volumes only)
    publication_places : list[PublicationPlace] | None
        Places where the volume was released (volumes only)
    part_of : list[PartOf] | None
        Parent publication(s) this belongs to
    bibliographical_notice : str | None
        HTML-formatted bibliographical notice
    homepage_url : HttpUrl | None
        URL of the website representing the publication
    download_urls : list[HttpUrl] | None
        URLs where the publication can be downloaded

    Examples
    --------
    >>> pub = Publication(
    ...     id="456",
    ...     type="volume",
    ...     title="Standard Catalog of World Coins",
    ...     year=2024,
    ...     isbn13="978-1234567890",
    ...     contributors=[
    ...         Contributor(role="author", name="George S. Cuhaj", id=123)
    ...     ]
    ... )
    >>> print(f"{pub.title} ({pub.year})")
    Standard Catalog of World Coins (2024)
    """

    # Required fields
    id: str = Field(..., description="Unique ID of the publication on Numista")
    type: Literal["volume", "article", "volume_group", "article_group"] = Field(
        ...,
        description="Type of publication",
    )

    # Core optional fields
    title: str | None = Field(None, description="Publication title")
    url: HttpUrl | None = Field(None, description="URL of the publication entry")
    translated_title: str | None = Field(None, description="Title translated into English")
    volume_number: str | None = Field(
        None,
        description="Volume number within group (volumes only)",
    )
    subtitle: str | None = Field(None, description="Subtitle (volumes only)")
    translated_subtitle: str | None = Field(
        None,
        description="Subtitle translated into English (volumes only)",
    )
    edition: str | None = Field(None, description="Edition information (volumes only)")
    languages: list[str] | None = Field(
        None,
        description="ISO 639 (alpha-2) language codes",
    )
    year: int | None = Field(None, description="Publication year")
    page_count: int | None = Field(None, description="Total number of pages (volumes only)")
    pages: str | None = Field(None, description="Page range (articles only)")
    cover: Literal["softcover", "hardcover", "spiral", "hidden_spiral"] | None = Field(
        None,
        description="Type of cover (volumes only)",
    )

    # Identifiers
    isbn10: str | None = Field(None, description="ISBN-10 code (volumes only)")
    isbn13: str | None = Field(None, description="ISBN-13 code (volumes only)")
    issn: str | None = Field(None, description="ISSN code (volume groups only)")
    oclc_number: str | None = Field(None, description="OCLC catalogue number")

    # Nested object arrays
    contributors: list[Contributor] | None = Field(
        None,
        description="List of contributors (authors, editors, translators)",
    )
    publishers: list[Publisher] | None = Field(
        None,
        description="Publisher information (volumes only)",
    )
    publication_places: list[PublicationPlace] | None = Field(
        None,
        description="Places where the volume was released (volumes only)",
    )
    part_of: list[PartOf] | None = Field(
        None,
        description="Parent publication(s) this belongs to",
    )

    # Additional metadata
    bibliographical_notice: str | None = Field(
        None,
        description="HTML-formatted bibliographical notice",
    )
    homepage_url: HttpUrl | None = Field(
        None,
        description="URL of the website representing the publication",
    )
    download_urls: list[HttpUrl] | None = Field(
        None,
        description="URLs where the publication can be downloaded",
    )
