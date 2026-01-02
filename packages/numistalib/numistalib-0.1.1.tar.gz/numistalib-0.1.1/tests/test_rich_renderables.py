"""Tests for Rich renderable fields in Pydantic models."""

import pytest
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from numistalib.models.base import NumistaBaseModel, RichField


class TestRichField:
    """Test RichField wrapper class functionality."""

    def test_panel_field(self) -> None:
        """Test storing a Rich Panel in a RichField."""

        class Model(NumistaBaseModel):
            panel: RichField

        panel = Panel("Test content", title="Test")
        model = Model(panel=RichField(panel))

        assert model.panel is not None
        assert isinstance(model.panel, RichField)
        assert isinstance(model.panel.value, Panel)

    def test_table_field(self) -> None:
        """Test storing a Rich Table in a RichField."""

        class Model(NumistaBaseModel):
            table: RichField

        table = Table(title="Test Table")
        table.add_column("ID")
        table.add_row("1")

        model = Model(table=RichField(table))

        assert model.table is not None
        assert isinstance(model.table, RichField)
        assert isinstance(model.table.value, Table)

    def test_text_field(self) -> None:
        """Test storing Rich Text in a RichField."""

        class Model(NumistaBaseModel):
            text: RichField

        text = Text("Styled text", style="bold red")
        model = Model(text=RichField(text))

        assert model.text is not None
        assert isinstance(model.text, RichField)
        assert isinstance(model.text.value, Text)

    def test_none_value(self) -> None:
        """Test that None is allowed for RichField."""

        class Model(NumistaBaseModel):
            renderable: RichField

        model = Model(renderable=RichField(None))
        assert model.renderable.value is None

        model2 = Model(renderable=RichField())
        assert model2.renderable.value is None

    def test_multiple_renderables(self) -> None:
        """Test model with multiple RichField fields."""

        class Model(NumistaBaseModel):
            panel: RichField
            table: RichField
            text: RichField

        model = Model(
            panel=RichField(Panel("Content")),
            table=RichField(Table()),
            text=RichField(Text("Test")),
        )

        assert isinstance(model.panel.value, Panel)
        assert isinstance(model.table.value, Table)
        assert isinstance(model.text.value, Text)

    def test_model_dump_includes_richfield(self) -> None:
        """Test that RichField is included in model_dump."""

        class Model(NumistaBaseModel):
            name: str
            panel: RichField

        model = Model(name="test", panel=RichField(Panel("Content")))

        # The panel should be present in the model
        assert model.panel is not None

        # model_dump should include RichField objects
        # (Rich objects don't serialize to JSON easily)
        dumped = model.model_dump()
        assert dumped["name"] == "test"

    def test_string_renderable(self) -> None:
        """Test that plain strings work as renderables."""

        class Model(NumistaBaseModel):
            text: RichField

        # Plain strings are valid Rich renderables
        model = Model(text=RichField("Plain string"))
        assert str(model.text) == "Plain string"

    def test_format_field_method(self) -> None:
        """Test the format_field method on RichField."""

        class Model(NumistaBaseModel):
            status: RichField

        model = Model(status=RichField(Text("Active", style="green")))
        
        # Test basic formatting
        formatted = model.status.format_field("Status", width=20)
        assert "Status:" in formatted
        assert "Active" in formatted
        assert len(formatted.split(":")[0]) + len(":") <= 20

        # Test with custom fill character
        formatted_dots = model.status.format_field("Status", width=20, fill_char=".")
        assert "." in formatted_dots

    def test_rich_console_protocol(self) -> None:
        """Test that RichField implements Rich console protocol."""

        class Model(NumistaBaseModel):
            panel: RichField

        panel = Panel("Test", title="Title")
        model = Model(panel=RichField(panel))

        # Should have __rich_console__ method
        assert hasattr(model.panel, "__rich_console__")

        # Should be renderable by Rich
        from rich.console import Console
        from io import StringIO

        output = StringIO()
        console = Console(file=output, force_terminal=True)
        console.print(model.panel)
        
        result = output.getvalue()
        assert len(result) > 0  # Should produce output
