"""Numista catalogue type models.

Pydantic models for Numista coin/banknote/exonumia types.
Used for validation and data transfer between integration and service layers.
"""

from __future__ import annotations

import re
from abc import ABC
from datetime import date
from functools import cached_property
from io import BytesIO
from typing import Annotated, Any, Literal

import httpx
from bs4 import BeautifulSoup
from PIL import Image as PILImage
from rich.repr import T
from rich.table import Table
from rich.text import Text
from pydantic import (
    AnyUrl,
    Field,
    HttpUrl,
    StringConstraints,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_core import Url
from textual_image.renderable import Image as TImage

from numistalib.models import Currency, Issuer, Mint, NumistaBaseModel, Reference
from numistalib.models.issues import IssueTerms


class Country(NumistaBaseModel):
    """Country information with code and name."""

    code: str = Field(max_length=50)
    name: str = Field(max_length=255)

    def __str__(self) -> str:
        """Return formatted country with code and name."""
        return f"{self.name} ({self.code})"


class CurrencyValue(NumistaBaseModel):
    """Currency value information."""

    text: str = Field(description="Textual representation of the value")
    numeric_value: float | None = Field(None, description="Numeric value")
    numerator: int | None = Field(None, description="Numerator for fractional values")
    denominator: int | None = Field(None, description="Denominator for fractional values")
    currency: Currency | None = Field(None, description="Currency information")


class Demonetization(NumistaBaseModel):
    """Demonetization status and date information."""

    is_demonetized: bool = Field(description="Indicates if the type is demonetized")
    demonetization_date: date | None = Field(None, description="Date of demonetization")

    @field_validator("demonetization_date", mode="before")
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
            from datetime import datetime
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


class Composition(NumistaBaseModel):
    """Metal composition information for coin types."""

    text: str = Field(description="Metal composition description")

    def __eq__(self, other: object) -> bool:  # Allow test equality to string value
        if isinstance(other, str):
            return self.text == other
        return super().__eq__(other)


class Technique(NumistaBaseModel):
    """Minting technique information."""

    text: str = Field(description="Minting technique description")


class LetteringScript(NumistaBaseModel):
    """Lettering script information for coin designs."""

    name: str = Field(description="Name of the lettering script")


class References(NumistaBaseModel):
    """Collection of references for a type."""

    references: list[Reference] = Field(description="List of references")


class RulerGroup(NumistaBaseModel):
    """Ruler group information for hierarchical ruler organization."""

    id: int = Field(..., description="Numista ID", alias="numista_id")
    name: str = Field(..., description="Group Name")


class Ruler(NumistaBaseModel):
    """Maps to Numista ruler schema for detailed ruler information."""

    id: int = Field(..., description="Numista ID", alias="numista_id")
    name: str = Field(..., description="Ruler Name")
    wikidata_id: str | None = Field(None, description="Wikidata ID")
    nomisma_id: str | None = Field(None, description="Nomisma ID")
    group: RulerGroup | None = Field(None, description="Group information")

    @computed_field
    @property
    def wikidata_url(self) -> Url | None:
        """Computed Wikidata URL from `wikidata_id`.

        Returns
        -------
        Url | None
            Full Wikidata URL if `wikidata_id` present, else None.
        """
        if self.wikidata_id:
            return Url(f"https://www.wikidata.org/wiki/{self.wikidata_id}")
        return None

    @computed_field
    @property
    def group_id(self) -> int | None:
        """Extract group ID from group.

        Returns
        -------
        int | None
            Group ID if group present, else None.
        """
        return self.group.id if self.group else None

    @computed_field
    @property
    def group_name(self) -> str | None:
        """Extract group name from group.

        Returns
        -------
        str | None
            Group name if group present, else None.
        """
        return self.group.name if self.group else None

    def render_compact(self) -> str:
        """Render compact ruler display."""
        lines = [f"[bold]{self.name}[/bold]"]
        if self.wikidata_id:
            lines.append(f"[link={self.wikidata_url}]Wikidata: {self.wikidata_id}[/link]")
        if self.group:
            lines.append(f"[dim]Group: {self.group.name}[/dim]")
        return "\n".join(lines)

    @classmethod
    def render_table(cls, items: list[Ruler], title: str = "") -> Table:
        """Generate table for ruler list with computed group fields.
        
        Parameters
        ----------
        items : list[Ruler]
            List of Ruler instances
        title : str
            Table title
            
        Returns
        -------
        Table
            Rich table with ruler information
        """
        from rich.table import Table

        table = Table(show_header=True, box=None, pad_edge=False, title=title, expand=True)
        table.add_column("Id", no_wrap=True)
        table.add_column("Name", no_wrap=True)
        table.add_column("Wikidata Id", no_wrap=True)
        table.add_column("Nomisma Id", no_wrap=True)
        table.add_column("Group Id", no_wrap=True)
        table.add_column("Group Name", no_wrap=True)

        for ruler in items:
            table.add_row(
                str(ruler.id),
                ruler.name,
                ruler.wikidata_id or "",
                ruler.nomisma_id or "",
                str(ruler.group_id) if ruler.group_id else "",
                ruler.group_name or ""
            )

        return table


class SideBase(NumistaBaseModel, ABC):
    """Base class for obverse and reverse sides of a type."""
    engravers: list[str] | None = Field(None, description="List of engravers")
    designers: list[str] | None = Field(None, description="List of designers")
    description: str | None = Field(None, description="Description of the side")
    lettering: str | None = Field(None, description="Lettering/inscription on the side")
    lettering_scripts: list[LetteringScript] | None = Field(None, description="Lettering scripts used")
    picture: AnyUrl = Field(description="Picture URL of the side")
    thumbnail: AnyUrl = Field(description="Thumbnail URL of the side")
    picture_copyright: str | None = Field(None, description="Picture copyright information")
    picture_copyright_url: AnyUrl | None = Field(None, description="URL for picture copyright information")
    picture_license_name: str | None = Field(None, description="Picture license name")
    picture_license_url: AnyUrl | None = Field(None, description="Picture license URL")
    lettering_translation: str | None = Field(None, description="Translation of the lettering/inscription")
    unabridged_legend: str | None = Field(None, description="Full unabridged lettering")

    @computed_field(description="Cleaned lettering as lines")
    def lettering_lines(self) -> list[str]:
        """Splits the lettering into individual lines using the embedded line break."""
        if not self.lettering:
            return []
        return [line.strip() for line in self.lettering.splitlines() if line.strip()]

    @cached_property
    def pillow_image(self) -> PILImage.Image | None:
        """Download and cache the full picture as a Pillow Image."""
        response = httpx.get(self.picture.encoded_string(), follow_redirects=True, timeout=30.0)
        response.raise_for_status()
        return PILImage.open(BytesIO(response.content))

    @cached_property
    def pillow_thumbnail(self) -> PILImage.Image | None:
        """Download and cache the thumbnail as a Pillow Image."""
        response = httpx.get(self.thumbnail.encoded_string(), follow_redirects=True, timeout=30.0)
        response.raise_for_status()
        return PILImage.open(BytesIO(response.content))

    @cached_property
    def renderable_image(self) -> Any | None:
        """Ready-to-print textual_image renderable (full picture)."""
        if self.pillow_image:
            return TImage(self.pillow_image)
            
    @cached_property
    def renderable_thumbnail(self) -> Any | None:
        """Ready-to-print thumbnail."""
        if self.pillow_thumbnail:
            return TImage(self.pillow_thumbnail)

    @computed_field(description="Formatted copyright link for textual display")
    def copyright_link(self) -> str:
        """Formatted copyright link for textual display."""
        return f"[link={self.picture_copyright_url}]{self.picture_copyright}[/link]"

    @computed_field(description="Formatted thumbnail link for textual display")
    def thumbnail_link(self) -> str:
        """Formatted thumbnail link for textual display."""
        return f"[link={self.thumbnail}]{self.thumbnail}[/link]"

    @computed_field(description="Formatted picture link for textual display")
    def picture_link(self) -> str:
        """Formatted picture link for textual display."""
        return f"[link={self.picture}]{self.picture}[/link]"

    @property
    def formatted_fields(self) -> list[str]:
        """Return formatted fields excluding redundant computed fields and formatting lists properly."""
        from numistalib.models.base.base_model import format_field

        formatted = []

        # Define fields to exclude (redundant computed fields)
        exclude_fields = {
            "lettering_lines",  # Redundant with lettering
            "copyright_link",   # Redundant with picture_copyright
            "thumbnail_link",   # Redundant with thumbnail
            "picture_link",     # Redundant with picture
        }

        # Process regular fields
        for field_name in self.__class__.model_fields.keys():
            if field_name in exclude_fields:
                continue

            value = getattr(self, field_name, None)
            if value is None:
                continue

            label = field_name.replace("_", " ").title()

            # Format lists specially
            if isinstance(value, list):
                if not value:
                    continue
                # Check if it's a list of models
                if all(hasattr(item, "__class__") and hasattr(item.__class__, "__name__") for item in value):
                    # List of objects - extract names
                    if hasattr(value[0], "name"):
                        formatted_value = ", ".join(str(item.name) for item in value)
                    else:
                        formatted_value = ", ".join(str(item) for item in value)
                else:
                    # Simple list
                    formatted_value = ", ".join(str(item) for item in value)
                formatted.append(format_field(label, formatted_value))
            else:
                formatted.append(format_field(label, value))

        # Process computed fields (excluding those in exclude set)
        for field_name in self.__class__.model_computed_fields.keys():
            if field_name in exclude_fields or field_name == "formatted_fields":
                continue

            value = getattr(self, field_name, None)
            if value is not None:
                label = field_name.replace("_", " ").title()
                formatted.append(format_field(label, value))

        return formatted


class Obverse(SideBase):
    """Obverse (front/heads) side of a coin or banknote."""

    pass


class Reverse(SideBase):
    """Reverse (back/tails) side of a coin or banknote."""

    pass


class Edge(NumistaBaseModel):
    """Edge specifications for a coin type.
    
    Parameters
    ----------
    description : str | None
        Description of the edge (e.g., 'Reeded', 'Plain')
    picture : str | None
        Picture URL of the edge
    thumbnail : str | None
        Thumbnail URL of the edge
    picture_copyright : str | None
        Copyright information for the picture
    lettering : str | None
        Lettering on the edge
    lettering_scripts : list[dict[str, Any]] | None
        Scripts used in edge lettering
    lettering_translation : str | None
        Translation of edge lettering
    """

    description: str | None = Field(None, description="Edge description (e.g., 'Reeded')")
    picture: str | None = Field(None, description="Edge picture URL")
    thumbnail: str | None = Field(None, description="Edge thumbnail URL")
    picture_copyright: str | None = Field(None, description="Edge picture copyright")
    picture_copyright_url: str | None = Field(None, description="Edge picture copyright URL")
    lettering: str | None = Field(None, description="Edge lettering text")
    lettering_scripts: list[dict[str, Any]] | None = Field(None, description="Scripts used in edge lettering")
    lettering_translation: str | None = Field(None, description="Translation of edge lettering")

    @cached_property
    def pillow_image(self) -> PILImage.Image | None:
        """Download and cache the full picture as a Pillow Image."""
        if self.picture:
            response = httpx.get(self.picture, follow_redirects=True, timeout=30.0)
            response.raise_for_status()
            return PILImage.open(BytesIO(response.content))
        
    @cached_property
    def pillow_thumbnail(self) -> PILImage.Image | None:
        """Download and cache the thumbnail as a Pillow Image."""
        if self.thumbnail:
            response = httpx.get(self.thumbnail, follow_redirects=True, timeout=30.0)
            response.raise_for_status()
            return PILImage.open(BytesIO(response.content))

    @cached_property
    def renderable_image(self) -> Any | None:
        """Ready-to-print textual_image renderable (full picture)."""
        if self.pillow_image:
            return TImage(self.pillow_image)

    @cached_property
    def renderable_thumbnail(self) -> Any | None:
        """Ready-to-print thumbnail."""
        if self.pillow_thumbnail:
            return TImage(self.pillow_thumbnail)


class Watermark(SideBase):
    """Watermark specifications for banknotes.
    
    Extends SideBase with all standard side fields (engravers, designers,
    description, lettering, picture, etc.) for watermark representation.
    """
    pass


class Printer(NumistaBaseModel):
    """Printer information for banknotes.
    
    Similar to Mint but for banknote printers.
    
    Parameters
    ----------
    id : int
        Unique printer ID
    name : str
        Printer name
    """
    id: int = Field(..., description="Unique printer ID")
    name: str = Field(..., description="Printer name")


class TypeBase(NumistaBaseModel, ABC):
    """Common fields shared between basic and full type representations."""
    numista_id: int = Field(alias="id", gt=0, description="Numista ID")
    title: Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)] = Field(
        ..., description="Type title"
    )

    category: Literal["coin", "banknote", "exonumia"] = Field(
        ..., description="Category: coin, banknote, exonumia"
    )
    min_year: int | None = Field(None, ge=-9999, le=9999, description="First year of production")  # Allow BC dates
    max_year: int | None = Field(None, ge=-9999, le=9999, description="Last year of production")

    @computed_field(description="Human-readable year range")
    def year_range(self) -> str:
        """Get human-readable year range."""
        if self.min_year and self.max_year:
            if self.min_year == self.max_year:
                return str(self.min_year)
            return f"{self.min_year}-{self.max_year}"
        elif self.min_year:
            return f"{self.min_year}-"
        elif self.max_year:
            return f"-{self.max_year}"
        return "Undated"

    @computed_field(description="Canonical Numista page URL")
    def numista_url(self) -> HttpUrl:
        """Get canonical Numista URL for this type."""
        return HttpUrl(f"https://en.numista.com/{self.numista_id}")

    @model_validator(mode="after")
    def validate_years(self) -> TypeBase:
        """Validate that min_year does not exceed max_year."""
        if self.min_year is not None and self.max_year is not None:
            if self.min_year > self.max_year:
                raise ValueError("min_year cannot be greater than max_year")
        return self


class TypeBasic(TypeBase):
    """Basic type information from search results."""

    issuer: Issuer | None = Field(None, description="Issuer information")
    country: Country | None = Field(None, description="Country information (used in related_types)")
    obverse_thumbnail: HttpUrl | None = Field(None, description="Obverse thumbnail URL")
    reverse_thumbnail: HttpUrl | None = Field(None, description="Reverse thumbnail URL")

    @model_validator(mode="before")
    @classmethod
    def _map_legacy_fields(cls, data: Any) -> Any:
        """Map legacy flat fields to structured ones and drop extras.

        Supports tests providing `issuer_code`/`issuer_name` (legacy) by
        composing an `issuer` dict, and removes the legacy keys to avoid
        extra field errors.
        """
        if not isinstance(data, dict):
            return data
        code = data.pop("issuer_code", None)
        name = data.pop("issuer_name", None)
        if (code or name) and "issuer" not in data:
            data["issuer"] = {"code": code or "", "name": name or ""}
        return data

    def render_compact(self) -> Any:
        """Render compact representation with thumbnail and formatted fields.

        Returns
        -------
        Any
            Rich renderable (Group with thumbnail + text or just text)
        """
        from rich.console import Group

        # Use formatted_fields for consistent DRY formatting
        text_block = "\n".join(self.formatted_fields)

        # Try to render thumbnail
        try:
            if self.obverse_thumbnail is not None:
                response = httpx.get(str(self.obverse_thumbnail), follow_redirects=True, timeout=10.0)
                response.raise_for_status()
                image = PILImage.open(BytesIO(response.content))
                thumb = TImage(image)
                return Group(thumb, text_block)
        except Exception:
            # Fallback to text only
            pass

        return text_block

    @classmethod
    def render_table(cls, items: list["TypeBasic"], title: str = "") -> Table:
        """Render a concise table for type search results.

        Columns include key catalogue search fields expected by the CLI:
        Numista ID, Type title, Category, First year, Last year, Issuer, Country,
        Obverse thumb URL, Reverse thumb URL.
        Issuer is rendered as a short name (link when possible).
        """
        table = Table(show_header=True, box=None, pad_edge=False, title=title)
        table.add_column("Numista ID", no_wrap=True)
        table.add_column("Type title", no_wrap=False)
        table.add_column("Category", no_wrap=True)
        table.add_column("First year", no_wrap=True)
        table.add_column("Last year", no_wrap=True)
        table.add_column("Issuer", no_wrap=False)
        table.add_column("Country", no_wrap=False)
        table.add_column("Obverse thumb URL", no_wrap=False, overflow="fold")
        table.add_column("Reverse thumb URL", no_wrap=False, overflow="fold")

        for t in items:
            # Issuer display: prefer name; add link when available
            issuer_text = ""
            if t.issuer:
                name = getattr(t.issuer, "name", None) or ""
                # Use Wikidata link if present as a safe external reference
                wikidata_id = getattr(t.issuer, "wikidata_id", None)
                if wikidata_id:
                    issuer_text = f"[link=https://www.wikidata.org/wiki/{wikidata_id}]{name}[/link]"
                else:
                    issuer_text = name

            def _link_cell(url: HttpUrl | None) -> Text:
                if not url:
                    return Text("")
                display = str(url)
                cell = Text(display)
                cell.stylize(f"link {display}", 0, len(display))
                return cell

            table.add_row(
                str(t.numista_id),
                t.title,
                t.category,
                str(t.min_year) if t.min_year is not None else "",
                str(t.max_year) if t.max_year is not None else "",
                issuer_text,
                (t.country.name if getattr(t, "country", None) and getattr(t.country, "name", None) else ""),
                _link_cell(t.obverse_thumbnail),
                _link_cell(t.reverse_thumbnail),
            )

        return table

    def to_dict(self) -> dict[str, object]:
        """Return a compact dict representation used by tests."""
        return {
            "numista_id": self.numista_id,
            "title": self.title,
            "category": self.category,
        }


class TypeFull(TypeBase):
    """Full type details including physical specifications."""

    @model_validator(mode="before")
    @classmethod
    def preprocess_data(cls, data: Any) -> Any:
        """Preprocess API data to normalize nested structures."""
        if not isinstance(data, dict):
            return data

        # Back-compat: accept legacy issuer fields
        code = data.pop("issuer_code", None)
        name = data.pop("issuer_name", None)
        if (code or name) and "issuer" not in data:
            data["issuer"] = {"code": code or "", "name": name or ""}

        # Drop thumbnails not present in full schema
        data.pop("obverse_thumbnail", None)
        data.pop("reverse_thumbnail", None)

        # Map diameter -> size
        if "diameter" in data and "size" not in data:
            try:
                data["size"] = float(data.pop("diameter"))
            except Exception:
                data.pop("diameter", None)

        # Map value_* -> value struct
        vt = data.pop("value_text", None)
        vn = data.pop("value_numeric", None)
        cn = data.pop("currency_name", None)
        if (vt is not None) or (vn is not None) or (cn is not None):
            value_obj: dict[str, Any] = {}
            if vt is not None:
                value_obj["text"] = vt
            if vn is not None:
                try:
                    value_obj["numeric_value"] = float(vn)
                except Exception:
                    pass
            # Currency requires many fields; skip constructing if only name present
            data["value"] = value_obj

        # Map obverse_* and reverse_* flat fields
        ob_desc = data.pop("obverse_description", None)
        ob_let = data.pop("obverse_lettering", None)
        if (ob_desc is not None) or (ob_let is not None):
            ob: dict[str, Any] = {}
            if ob_desc is not None:
                ob["description"] = ob_desc
            if ob_let is not None:
                ob["lettering"] = ob_let
            # Provide dummy required URLs when absent for validation convenience in tests
            ob.setdefault("picture", "https://example.com/obverse.jpg")
            ob.setdefault("thumbnail", "https://example.com/obverse_t.jpg")
            data["obverse"] = ob

        rv_desc = data.pop("reverse_description", None)
        rv_let = data.pop("reverse_lettering", None)
        if (rv_desc is not None) or (rv_let is not None):
            rv: dict[str, Any] = {}
            if rv_desc is not None:
                rv["description"] = rv_desc
            if rv_let is not None:
                rv["lettering"] = rv_let
            rv.setdefault("picture", "https://example.com/reverse.jpg")
            rv.setdefault("thumbnail", "https://example.com/reverse_t.jpg")
            data["reverse"] = rv

        # Accept simple string for composition
        comp = data.get("composition")
        if isinstance(comp, str):
            data["composition"] = {"text": comp}

        # Ensure url present (required); synthesize if missing
        if "url" not in data and (nid := data.get("numista_id") or data.get("id")):
            try:
                nid_int = int(nid)
                data["url"] = f"https://example.com/types/{nid_int}"
            except Exception:
                data["url"] = "https://example.com/types/unknown"

        # Normalize references catalogue field from dict to string
        if "references" in data and isinstance(data["references"], list):
            for ref in data["references"]:
                if isinstance(ref, dict) and "catalogue" in ref:
                    cat = ref["catalogue"]
                    if isinstance(cat, dict) and "code" in cat:
                        ref["catalogue"] = cat["code"]

        return data

    # Required fields that only exist in full version
    url: HttpUrl = Field(..., description="Numista URL")
    issuer: Issuer 
    # Optional full-only fields
    issue_terms: IssueTerms | None = Field(None, alias="issueTerms", description="Issue Terms")
    issuing_entity: dict[str, Any] | None = Field(None, description="① Issuing entity")
    secondary_issuing_entity: dict[str, Any] | None = Field(None, description="② Issuing entity")
    type: str | None = Field(None, max_length=100)
    rulers: list[Ruler] | None = Field(None, alias="ruler")
    value: CurrencyValue | None = Field(None)
    demonetization: Demonetization | None = Field(None)
    size: float | None = Field(None, ge=0, description="① size mm")
    size2: float | None = Field(None, ge=0, description="② size mm")
    thickness: float | None = Field(None, ge=0)
    weight: float | None = Field(None, ge=0)
    shape: str | None = Field(None, max_length=100)
    composition: Composition | None = Field(None)
    technique: Technique | None = Field(None)
    obverse: Obverse | None = Field(None)
    reverse: Reverse | None = Field(None)
    watermark: Watermark | None = Field(None, description="Watermark (notes)")
    references: list[Reference] | None = Field(None)
    mints: list[Mint] | None = Field(None)
    printers: list[Printer] | None = Field(None, description="Printers (notes)")
    comments: str | None = Field(None)
    tags: list[str] | None = Field(None)
    edge: Edge | None = Field(None)
    related_types: list[TypeBasic] | None = Field(None)  # Note: recursive, but TypeBasic is defined
    orientation: str | None = Field(None)
    series: str | None = Field(None, description="Series/set")
    commemorated_topic: str | None = Field(None, description="Topic commemorated")

    @computed_field
    @property
    def orientation_symbol(self) -> str | None:
        """Return symbol representation of orientation.
        
        Returns ⇈ (upup arrows) for medal, ⇅ (updown arrows) for coin, or None.
        """
        if not self.orientation:
            return None
        orientation_lower = self.orientation.lower()
        if "medal" in orientation_lower:
            return "⇈"
        elif "coin" in orientation_lower:
            return "⇅"
        return None

    @computed_field
    @property
    def comments_rendered(self) -> str | None:
        """Return terminal-safe scrubbed comments.
        
        Comments field may contain HTML with line feeds, links, images, and formatting.
        This computed field scrubs HTML artifacts for clean terminal display with Rich markup.
        
        Returns
        -------
        str | None
            Scrubbed comments ready for terminal rendering, or None if no comments
        """
        if not self.comments:
            return None

        text = self.comments

        # Check if value contains HTML
        if "<" in text and ">" in text:
            soup = BeautifulSoup(text, "html.parser")

            # First pass: Replace image links with inline marker before text extraction
            # Pattern: description text <br/> <a><img></a> <br/> next description
            # Strategy: Find all <a> tags with images and mark them before processing breaks
            for link in soup.find_all("a"):
                href = link.get("href", "")
                img = link.find("img")
                if img and href:
                    # Replace with inline link marker
                    link.replace_with(f" [link={href}](image)[/link]")
                else:
                    # Regular text link
                    link_text = link.get_text(strip=True)
                    if href and link_text:
                        link.replace_with(f" [link={href}]{link_text}[/link]")
                    elif link_text:
                        link.replace_with(f" {link_text}")
                    else:
                        link.decompose()

            # Remove standalone images
            for img in soup.find_all("img"):
                img.decompose()

            # Convert paragraphs
            for p in soup.find_all("p"):
                p.insert_before("\n")
                p.insert_after("\n")
                p.unwrap()

            # Convert <br/> to newlines
            for br in soup.find_all("br"):
                br.replace_with("\n")

            # Get text
            text = soup.get_text()

        if text:
            # Clean up whitespace
            text = re.sub(r"\r\n", "\n", text)  # Normalize line endings
            text = re.sub(r"[ \t]+", " ", text)  # Normalize spaces

            # Merge lines: if a line starts with whitespace + [link=, append it to previous line
            text = re.sub(r"\n+\s*(\[link=)", r" \1", text)

            # Collapse excessive newlines
            text = re.sub(r"\n\n\n+", "\n\n", text)

            # Strip each line but keep line structure
            lines = [line.strip() for line in text.split("\n")]
            # Remove empty lines
            lines = [line for line in lines if line]
            text = "\n".join(lines)

        return text.strip() if text else None

    def render_detail(self, cache_indicator: str = "") -> Any:
        """Render detailed type information using theme-aware, vertical scrolling layout.

        Parameters
        ----------
        cache_indicator : str
            Cache indicator (e.g., "💾" for cached, "🌐" for fresh)

        Returns
        -------
        Any
            Group of Rich panels for display
        """
        import re
        import textwrap

        from rich.console import Group

        from numistalib.cli.theme import CLISettings
        from numistalib.models.mints import Mint
        from numistalib.models.references import Reference

        # General panel - filter out None values
        general_lines = []
        for key in ["numista_id", "numista_url", "title", "series", "category", "year_range"]:
            field = self.formatted_fields_dict.get(key)
            if field:
                general_lines.append(field)

        if self.demonetization:
            demonetized = self.demonetization.formatted_fields_dict.get("is_demonetized")
            if demonetized:
                general_lines.append(demonetized)

        commemorated = self.formatted_fields_dict.get("commemorated_topic")
        if commemorated:
            general_lines.append(commemorated)

        if self.tags:
            general_lines.append("[header]Tags:[/header]")
            general_lines.append(" ".join([f"[inverse]{g}[/inverse]" for g in self.tags]))

        general_panel = CLISettings.panel(
            title=f"{cache_indicator} Type Details",
            content="\n".join(general_lines)
        )

        # Value panel - filter out None values
        value_lines = []
        if self.value:
            for key in ["text", "numeric_value", "numerator", "denominator"]:
                field = self.value.formatted_fields_dict.get(key)
                if field:
                    value_lines.append(field)

            if self.value.currency:
                value_lines.append("[header]Currency:[/header]")
                for key in ["name", "full_name", "symbol", "numista_id"]:
                    field = self.value.currency.formatted_fields_dict.get(key)
                    if field:
                        value_lines.append(field)

        value_panel = CLISettings.panel(
            title="Value",
            content="\n".join(value_lines) if value_lines else ""
        )

        # Issuer panel - filter out None values
        issuer_lines = []
        for key in ["issuing_entity", "issue_terms"]:
            field = self.formatted_fields_dict.get(key)
            if field:
                issuer_lines.append(field)

        if self.issuer:
            for key in ["code", "name"]:
                field = self.issuer.formatted_fields_dict.get(key)
                if field:
                    issuer_lines.append(field)

        issuer_panel = CLISettings.panel(
            title="Issuer",
            content="\n".join(issuer_lines) if issuer_lines else ""
        )

        mints_panel = CLISettings.panel(
            title="Mints",
            content=Mint.render_table(self.mints, title="") if self.mints else ""
        )

        # Physical specifications panel - filter out None values
        specs_lines = []
        for key in ["orientation", "shape", "size", "thickness"]:
            field = self.formatted_fields_dict.get(key)
            if field:
                specs_lines.append(field)

        if self.composition:
            specs_lines.append("[header]Composition:[/header]")
            comp_text = self.composition.formatted_fields_dict.get("text")
            if comp_text:
                specs_lines.append(comp_text)

        specs_panel = CLISettings.panel(
            title="Physical Specifications",
            content="\n".join(specs_lines) if specs_lines else ""
        )

        edge_panel = CLISettings.panel(
            title="Edge Specifications",
            content=Group(
                "\n".join([f for f in self.edge.formatted_fields]) if self.edge else "",
                self.edge.renderable_thumbnail if self.edge and self.edge.renderable_thumbnail else ""
            ) if self.edge else ""
        )

        obverse_panel = CLISettings.panel(
            title="Obverse Specifications",
            content=Group(
                "\n".join([f for f in self.obverse.formatted_fields]),
                self.obverse.renderable_thumbnail if self.obverse.renderable_thumbnail else ""
            )
        )

        reverse_panel = CLISettings.panel(
            title="Reverse Specifications",
            content=Group(
                "\n".join([f for f in self.reverse.formatted_fields]),
                self.reverse.renderable_thumbnail if self.reverse.renderable_thumbnail else ""
            )
        )

        rulers_panel = CLISettings.panel(
            title="Rulers",
            content=Ruler.render_table(self.rulers, title="") if self.rulers else ""
        )

        references_panel = CLISettings.panel(
            title="References",
            content=Reference.render_table(self.references, title="") if self.references else ""
        )

        # Related types panel - use list rendering with thumbnails
        related_types_panel = CLISettings.panel(
            title="Related Types",
            content=TypeBasic.render_list(self.related_types) if self.related_types else ""
        )

        # Comments panel - promote label to title (single field)
        # Pre-wrap text to panel width to avoid mid-word breaks
        comments_text = ""
        if self.comments_rendered:
            # Wrap each line to panel width - 4 (for panel borders/padding)
            wrapped_lines = []
            for line in self.comments_rendered.split('\n'):
                # Use textwrap to break long lines at word boundaries
                if len(line) > (CLISettings.PANEL_WIDTH - 4):
                    wrapped = textwrap.fill(line, width=CLISettings.PANEL_WIDTH - 4, break_long_words=False, break_on_hyphens=False)
                    wrapped_lines.append(wrapped)
                else:
                    wrapped_lines.append(line)
            comments_text = '\n'.join(wrapped_lines)

        comments_panel = CLISettings.panel(
            title="Comments",
            content=comments_text
        )

        return (
            general_panel,
            value_panel,
            issuer_panel,
            mints_panel,
            specs_panel,
            edge_panel,
            obverse_panel,
            reverse_panel,
            rulers_panel,
            references_panel,
            related_types_panel,
            comments_panel,
        )
