"""Base models for all Numista entities.

Common configuration, behavior, and abstract base classes for Pydantic models.
"""
import re
from abc import ABC
from typing import Any, Self, Iterable

import rich.repr
from bs4 import BeautifulSoup
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from rich.console import Group, RenderableType
from rich.console import Console, ConsoleOptions
from rich.text import Text
from pydantic_core import core_schema

# Panel formatting constants
PANEL_VALUE_COLUMN: int = 20
PANEL_HANGING_INDENT: int = 5


def safe(val: Any, default: str = "") -> str:
        """Return string representation or default if None or empty."""
        return val if val is not None and str(val).strip() else default


def scrub(value: Any) -> str:
    """Scrub HTML from field values, preserving formatting.

    Uses BeautifulSoup4 to detect paragraphs, breaks, and links,
    converting them to appropriate plain text with Rich markup.

    Parameters
    ----------
    value : Any
        Field value (may contain HTML)

    Returns
    -------
    str
        Cleaned value with Rich markup for links
    """
    text = safe(value)

    if not type(text) == str:
        return str(text)

    # Check if value contains HTML
    if ("<" in text and ">" in text):
        soup = BeautifulSoup(text, "html.parser")

        # Convert paragraphs to double newlines
        for p in soup.find_all("p"):
            p.replace_with(f"{p.get_text(strip=False)}\n")

        # Convert breaks to single newlines
        for br in soup.find_all("br"):
            br.replace_with("\n")

        # Fix links - convert to Rich markup
        for link in soup.find_all("a"):
            href = link.get("href", "")
            link_text = link.get_text()
            if href:
                link.replace_with(f"[link={href}]{link_text}[/link]")
            else:
                link.replace_with(link_text)

        # Get cleaned text
        text = soup.get_text()

    if text:
        # clean up whitespace
        text = re.sub(r"\n\n\n+", "\n\n", text.strip())  # collapse multiple newlines
        text = re.sub(r"[ \t]+", " ", text)

        # look for line feeds
        cleaned_lines = [l.strip() for l in text.split("\n")]
        text = "\n".join(cleaned_lines)

    return text.strip()


def format_field(
        label: str,
        value: Any,
        value_column: int | None = None,
        hanging_indent: int | None = None,
        short_line_field_separator: str = " "
    ) -> str:
    """Format a single field with label and value using Rich markup.

    Applies intelligent formatting based on value length and content:
    - Short values (≤25 chars): Same line, aligned at value_column
    - Long values (>25 chars): Next line at column 1
    - Multiline values: Indented at 'indent' columns, extra linefeed after

    Parameters
    ----------
    label : str
        Field label
    value : Any
        Field value
    value_column : int | None
        Column where values start (default: uses panel_value_column class property)
    indent : int | None
        Indentation for multiline values (default: uses hanging_indent class property)

    Returns
    -------
    str
        Formatted field string with Rich markup and proper alignment
    """
    # Use class properties as defaults
    value_column = value_column if value_column is not None else PANEL_VALUE_COLUMN
    hanging_indent = hanging_indent if hanging_indent is not None else PANEL_HANGING_INDENT

    # Scrub HTML and get cleaned value
    cleaned_value = scrub(value)

    # Format label with Rich markup
    formatted_label = f"[label]{label}:[/label]"

    # Detect multiline content
    is_multiline = "\n" in cleaned_value
    value_length = len(cleaned_value.split("\n")[0]) if is_multiline else len(cleaned_value)

    if is_multiline:
        # Multiline: indent each line, add extra linefeed at end
        lines = cleaned_value.split("\n")
        indent_str = " " * hanging_indent
        indented_lines = [f"{indent_str}{line}" for line in lines]
        formatted_value = "\n".join(indented_lines)
        return f"{formatted_label}\n{formatted_value}\n"

    elif value_length > 25:
        # Long single-line: start on next line at column 1, add extra linefeed
        return f"{formatted_label}\n{cleaned_value}\n"

    else:
        # Short value: same line, aligned at value_column
        # Calculate padding to align value at value_column
        label_width = len(label) + 1  # +1 for the colon
        padding_needed = max(1, value_column - label_width)
        padding = short_line_field_separator * padding_needed
        return f"{formatted_label}{padding}[value]{cleaned_value}[/value]"


class NumistaBaseModel(ABC, BaseModel):
    """Base model for all Numista entities.

    Provides a shared Pydantic base configuration with:
    - Strict validation
    - Immutability control
    - Extra field prohibition
    - Consistent configuration
    """

    model_config = ConfigDict(
        strict=True,
        frozen=False,
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=False,
        populate_by_name=True,
        alias_generator=to_camel,
        use_enum_values=True,
    )

    def __rich_repr__(self) -> rich.repr.Result:
        """Make models look good when printed with rich.print()."""
        for name, field in self.__class__.model_fields.items():
            value = getattr(self, name)
            if value is None:  # Skip None fields for cleaner output
                continue
            if field.alias:
                yield field.alias, value
            else:
                yield name, value

    def to_api_dict(self, **kwargs: Any) -> dict[Any, Any]:
        """Return dict suitable for sending back to API or clean export.
        Uses aliases, excludes None by default.
        """
        return self.model_dump(
            by_alias=kwargs.get("by_alias", True),
            exclude_none=kwargs.get("exclude_none", True),
            exclude_unset=kwargs.get("exclude_unset", True),
            **kwargs,
        )

    @property
    def formatted_fields_dict(self) -> dict[str, str]:
        """Return dictionary of formatted strings for all model fields.

        Automatically formats all fields (regular and computed) in the model
        using format_field() with default column alignment and indentation.

        Returns
        -------
        dict[str, str]
            Dictionary mapping field names to formatted field strings
        """
        formatted: dict[str, str] = {}

        # Get all model fields including computed fields
        for field_name in self.__class__.model_fields.keys():
            value = getattr(self, field_name, None)
            if value is not None:  # Skip None values
                # Convert field name to human-readable label
                label = field_name.replace("_", " ").title()
                formatted[field_name] = format_field(label, value)

        # Also include computed fields
        for field_name in self.__class__.model_computed_fields.keys():
            if field_name in ("panel_template", "formatted_fields_dict"):
                continue  # Skip these special fields
            value = getattr(self, field_name, None)
            if value is not None:
                label = field_name.replace("_", " ").title()
                formatted[field_name] = format_field(label, value)

        return formatted

    @property
    def formatted_fields(self) -> list[str]:
        """Return list of formatted strings for all model fields.

        Automatically formats all fields (regular and computed) in the model
        using format_field() with default column alignment and indentation.

        Returns
        -------
        list[str]
            List of formatted field strings
        """
        return list(self.formatted_fields_dict.values())

    # def formatted_fields_deep(self) -> dict[str, str]:
    #     """Return formatted fields and recurse into related model lists without tables."""
    #     formatted: dict[str, str] = {}

    #     def process_field(field_name: str, value: Any) -> None:
    #         if value is None:
    #             return

    def render_compact(self) -> RenderableType:
        """Render compact representation for grid display.

        Default implementation returns formatted title and key metadata.
        Override in subclasses for custom compact display.

        Returns
        -------
        RenderableType
            Compact renderable for grid/column layout
        """
        # Get a simple text representation with key fields
        lines: list[str] = []
        
        # Try to get a primary identifier
        title = getattr(self, 'title', None)
        if title is not None:
            lines.append(str(title))
        else:
            name = getattr(self, 'name', None)
            if name is not None:
                lines.append(str(name))
            else:
                numista_id = getattr(self, 'numista_id', None)
                if numista_id is not None:
                    lines.append(f"ID: {numista_id}")
        
        # Add secondary info if available
        year = getattr(self, 'year', None)
        if year is not None:
            lines.append(f"Year: {year}")
        else:
            min_year = getattr(self, 'min_year', None)
            max_year = getattr(self, 'max_year', None)
            if min_year is not None and max_year is not None:
                year_info = str(min_year) if min_year == max_year else f"{min_year}-{max_year}"
                lines.append(f"Years: {year_info}")
        
        country = getattr(self, 'country', None)
        if country is not None:
            country_name = getattr(country, 'name', None)
            if country_name is not None:
                lines.append(str(country_name))
            else:
                lines.append(str(country))
        else:
            issuer = getattr(self, 'issuer', None)
            if issuer is not None:
                issuer_name = getattr(issuer, 'name', None)
                if issuer_name is not None:
                    lines.append(str(issuer_name))
                else:
                    lines.append(str(issuer))
        
        return "\n".join(lines) if lines else str(self)

    @classmethod
    def render_list(cls, items: list[Self]) -> Group | str:
        """Render list of items as Rich Group with horizontal rule separators.
        
        Helper for CLI list rendering. Calls render_compact() on each item
        and adds horizontal rules between items when there are multiple.
        
        Parameters
        ----------
        items : list[Self]
            List of model instances to render
            
        Returns
        -------
        Group | str
            Rich Group containing all items with separators, or message if empty
        """
        if not items:
            return "No items available"
        
        content: list[RenderableType] = []
        for i, item in enumerate(items):
            content.append(item.render_compact())
            # Add horizontal rule separator between items (not after last)
            if i < len(items) - 1:
                content.append("")  # Blank line
                content.append("─" * 80)  # Horizontal rule
                content.append("")  # Blank line
        
        return Group(*content)

    def as_panel(self, style_overrides: dict[str, Any] | None = None) -> Any:
        """Render model as Rich Panel.
        
        Default implementation creates a panel with formatted fields.
        Override in subclasses for custom panel layout.
        
        Parameters
        ----------
        style_overrides : dict[str, Any] | None
            Optional style overrides for the panel
            
        Returns
        -------
        Panel
            Rich Panel with model data
        """
        from numistalib.cli.theme import CLISettings
        
        # Get formatted fields as content
        content = "\n".join(self.formatted_fields)
        
        # Get title (try common field names)
        title = None
        for field_name in ["title", "name", "code"]:
            if hasattr(self, field_name):
                title = getattr(self, field_name)
                break
        
        if not title:
            title = self.__class__.__name__
        
        return CLISettings.panel(content=content, title=str(title))


class RichField:
    """Wrapper for Rich renderables to use as Pydantic fields.

    Stores any Rich renderable (Panel, Table, Text, or plain string/None)
    and implements the Rich console protocol for direct rendering.

    Also provides a simple `format_field` helper used by tests to produce
    aligned label/value output.
    """

    def __init__(self, value: Any | None = None) -> None:
        self.value = value

    def __str__(self) -> str:
        if self.value is None:
            return ""
        return str(self.value)

    # Rich console protocol
    def __rich_console__(self, console: Console, options: ConsoleOptions) -> Iterable[RenderableType]:
        if self.value is None:
            yield Text("")
        elif isinstance(self.value, (str, Text)):
            yield self.value if isinstance(self.value, Text) else Text(self.value)
        else:
            # Assume it's a Rich renderable; let Rich handle it
            yield self.value  # type: ignore[misc]

    def format_field(self, label: str, width: int = 20, fill_char: str = " ") -> str:
        """Return a simple one-line formatted label/value string.

        Parameters
        ----------
        label : str
            Field label to display before the value
        width : int
            Column at which value starts (minimum)
        fill_char : str
            Character used to pad between label and value
        """
        label_text = f"{label}:"
        pad_len = max(0, width - len(label_text))
        padding = fill_char * pad_len
        return f"{label_text}{padding}{self.__str__()}"

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> core_schema.CoreSchema:  # type: ignore[name-defined]
        """Pydantic v2 integration: accept any input and wrap as RichField.

        Allows using `RichField` as a typed field without enabling
        `arbitrary_types_allowed` globally.
        """
        def _validate(value: Any) -> "RichField":
            return value if isinstance(value, RichField) else RichField(value)

        return core_schema.no_info_after_validator_function(
            _validate,
            core_schema.any_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(str, when_used="json"),
        )

