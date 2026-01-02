"""Numista collections models.

Pydantic models for Numista user collections.
"""

from datetime import date as date_type
from typing import Literal

from pydantic import Field, HttpUrl, computed_field

from numistalib.models.base import NumistaBaseModel


class UserCollection(NumistaBaseModel):
    """User-defined collection container.

    Represents a named collection that groups collected items for a user.
    """

    id: int = Field(..., gt=0, alias="numista_id", description="Numista collection ID")
    name: str = Field(..., description="Collection name")

    def to_dict(self) -> dict[str, object]:
        """Convert collection to dictionary representation."""
        return self.model_dump()


class TypeDetail(NumistaBaseModel):
    """Type detail for collected items.

    Parameters
    ----------
    id : int
        ID of the type
    title : str
        Title of the type
    category : Literal["coin", "banknote", "exonumia"]
        Category
    issuer : dict | None
        Issuer information (code, name)
    """

    id: int = Field(..., description="ID of the type")
    title: str = Field(..., description="Title of the type")
    category: Literal["coin", "banknote", "exonumia"] = Field(..., description="Category")
    issuer: dict[str, str] | None = Field(None, description="Issuer information")


class Picture(NumistaBaseModel):
    """Picture or PDF document.

    Parameters
    ----------
    url : HttpUrl
        URL to the picture or document in original size
    thumbnail_url : HttpUrl
        URL to the thumbnail
    """

    url: HttpUrl = Field(..., description="URL to the picture or document")
    thumbnail_url: HttpUrl = Field(..., description="URL to the thumbnail")


class GradingCompany(NumistaBaseModel):
    """Grading company information.

    Parameters
    ----------
    id : int
        ID of the grading service in Numista
    name : str
        Name of the grading service
    """

    id: int = Field(..., description="ID of the grading service")
    name: str = Field(..., description="Name of the grading service")


class SlabGrade(NumistaBaseModel):
    """Slab grade information.

    Parameters
    ----------
    id : int
        ID of the grading mark in Numista
    value : str
        Value of the grading mark
    """

    id: int = Field(..., description="ID of the grading mark")
    value: str = Field(..., description="Value of the grading mark")


class GradingDesignation(NumistaBaseModel):
    """Grading designation.

    Parameters
    ----------
    id : int
        ID of the grading designation in Numista
    value : str
        Value of the grading designation
    """

    id: int = Field(..., description="ID of the grading designation")
    value: str = Field(..., description="Value of the grading designation")


class GradingStrike(NumistaBaseModel):
    """Grading strike information.

    Parameters
    ----------
    id : int
        ID of the grading strike in Numista
    value : str
        Value of the grading strike
    """

    id: int = Field(..., description="ID of the grading strike")
    value: str = Field(..., description="Value of the grading strike")


class GradingSurface(NumistaBaseModel):
    """Grading surface information.

    Parameters
    ----------
    id : int
        ID of the grading surface in Numista
    value : str
        Value of the grading surface
    """

    id: int = Field(..., description="ID of the grading surface")
    value: str = Field(..., description="Value of the grading surface")


class GradingDetails(NumistaBaseModel):
    """Professional grading details.

    Parameters
    ----------
    grading_company : GradingCompany | None
        Grading service information
    slab_grade : SlabGrade | None
        Slab grade information
    slab_number : str | None
        Slab number
    cac_sticker : Literal["Green", "Gold"] | None
        CAC sticker type
    grading_designations : list[GradingDesignation] | None
        List of grading designations
    grading_strike : GradingStrike | None
        Grading strike information
    grading_surface : GradingSurface | None
        Grading surface information
    """

    grading_company: GradingCompany | None = Field(None, description="Grading service")
    slab_grade: SlabGrade | None = Field(None, description="Slab grade")
    slab_number: str | None = Field(None, description="Slab number")
    cac_sticker: Literal["Green", "Gold"] | None = Field(None, description="CAC sticker")
    grading_designations: list[GradingDesignation] | None = Field(
        None,
        description="Grading designations",
    )
    grading_strike: GradingStrike | None = Field(None, description="Grading strike")
    grading_surface: GradingSurface | None = Field(None, description="Grading surface")


class CollectedItem(NumistaBaseModel):
    """Item in a user's collection.

    Maps to Numista collected_item entity with full swagger specification.

    Parameters
    ----------
    id : int
        Unique ID of the item
    quantity : int
        Quantity of items
    type : TypeDetail
        Type details (id, title, category, issuer)
    for_swap : bool
        Available for swap
    issue : dict | None
        Issue information (full issue object)
    grade : Literal | None
        Grade (g, vg, f, vf, xf, au, unc)
    private_comment : str | None
        Private comment (auth required)
    public_comment : str | None
        Public comment
    price : dict | None
        Price object reference
    collection : UserCollection | None
        Parent collection reference
    pictures : list[Picture] | None
        Pictures or PDF documents
    storage_location : str | None
        Storage location
    acquisition_place : str | None
        Acquisition place
    acquisition_date : date_type | None
        Date acquired (YYYY-MM-DD)
    serial_number : str | None
        Serial number
    internal_id : str | None
        Internal ID
    weight : float | None
        Weight in grams
    size : float | None
        Size in millimeters
    axis : int | None
        Die axis (1-12, h notation)
    grading_details : GradingDetails | None
        Professional grading information
    """

    # Required fields
    id: int = Field(..., description="Unique ID of the item")
    quantity: int = Field(..., description="Quantity of items")
    type: TypeDetail = Field(..., description="Type details")
    for_swap: bool = Field(..., description="Available for swap")

    # Optional core fields
    issue: dict[str, object] | None = Field(None, description="Issue information")
    grade: Literal["g", "vg", "f", "vf", "xf", "au", "unc"] | None = Field(
        None,
        description="Grade",
    )
    private_comment: str | None = Field(None, description="Private comment")
    public_comment: str | None = Field(None, description="Public comment")
    price: dict[str, object] | None = Field(None, description="Price information")
    collection: UserCollection | None = Field(None, description="Parent collection")
    pictures: list[Picture] | None = Field(None, description="Pictures or PDFs")

    # Location and acquisition
    storage_location: str | None = Field(None, description="Storage location")
    acquisition_place: str | None = Field(None, description="Acquisition place")
    acquisition_date: date_type | None = Field(None, description="Date acquired")

    # Identifiers and measurements
    serial_number: str | None = Field(None, description="Serial number")
    internal_id: str | None = Field(None, description="Internal ID")
    weight: float | None = Field(None, description="Weight in grams")
    size: float | None = Field(None, description="Size in millimeters")
    axis: int | None = Field(None, ge=1, le=12, description="Die axis (1-12)")

    # Professional grading
    grading_details: GradingDetails | None = Field(
        None,
        description="Professional grading information",
    )

    @computed_field(description="Type ID for backwards compatibility")
    def type_id(self) -> int:
        """Extract type ID from type object."""
        return self.type.id

    @computed_field(description="Issue ID for backwards compatibility")
    def issue_id(self) -> int | None:
        """Extract issue ID from issue object."""
        if self.issue and "id" in self.issue:
            issue_id_val = self.issue["id"]
            if isinstance(issue_id_val, int):
                return issue_id_val
            return int(str(issue_id_val))
        return None

    @computed_field(description="Item summary for display")
    def item_summary(self) -> str:
        """Summary of collected item."""
        parts = [f"{self.type.title}"]
        if self.quantity > 1:
            parts.append(f"x{self.quantity}")
        if self.grade:
            parts.append(f"({self.grade})")
        return " ".join(parts)
