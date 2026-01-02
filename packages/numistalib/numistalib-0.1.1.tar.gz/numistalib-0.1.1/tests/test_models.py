"""Tests for Numista models."""

import pytest
from pydantic import ValidationError

from numistalib.models.catalogues import Catalogue
from numistalib.models.issuer import Issuer
from numistalib.models.types import TypeBasic, TypeFull

TEST_NUMISTA_ID: int = 95420
TEST_WEIGHT: float = 28.8


def test_type_basic_valid() -> None:
    """Test TypeBasic with valid data."""
    type_basic = TypeBasic(
        numista_id=95420,
        title="1 Thaler",
        category="coin",
        issuer_code="muhlhausen",
        issuer_name="Mühlhausen",
        min_year=1622,
        max_year=1622,
        obverse_thumbnail="https://example.com/obverse.png",
        reverse_thumbnail="https://example.com/reverse.png",
    )
    assert type_basic.numista_id == TEST_NUMISTA_ID
    assert type_basic.title == "1 Thaler"
    assert type_basic.category == "coin"


def test_type_basic_missing_required() -> None:
    """Test TypeBasic validation with missing required title field."""
    with pytest.raises(ValidationError):
        TypeBasic(  # type: ignore
            numista_id=95420,
            category="coin",
            issuer_code="muhlhausen",
            issuer_name="Mühlhausen",
            min_year=1622,
            max_year=1622,
            obverse_thumbnail="https://example.com/obverse.png",
            reverse_thumbnail="https://example.com/reverse.png",
        )


def test_type_full_extends_basic() -> None:
    """Test TypeFull inherits from TypeBasic."""
    type_full = TypeFull(
        numista_id=95420,
        title="1 Thaler",
        category="coin",
        issuer_code="muhlhausen",
        issuer_name="Mühlhausen",
        min_year=1622,
        max_year=1622,
        obverse_thumbnail="https://example.com/obverse.png",
        reverse_thumbnail="https://example.com/reverse.png",
        composition="Silver",
        weight=28.8,
        diameter=42.0,
        value_text="1",
        value_numeric=1.0,
        currency_name="Thaler",
        thickness=2.5,
        obverse_description="",
        obverse_lettering="",
        reverse_description="",
        reverse_lettering="",
    )
    assert type_full.numista_id == TEST_NUMISTA_ID
    assert type_full.composition == "Silver"
    assert type_full.weight == TEST_WEIGHT


def test_catalogue_valid() -> None:
    """Test Catalogue model with valid data."""
    catalogue = Catalogue(  # type: ignore
        numista_id=1,
        code="KM",
        title="Krause World Coins",
    )
    assert catalogue.code == "KM"
    assert catalogue.title == "Krause World Coins"


def test_issuer_valid() -> None:
    """Test Issuer model with valid data."""
    issuer = Issuer(
        code="united-states",
        name="United States",
        flag="https://example.com/flag.png",
        level=1,
    )
    assert issuer.code == "united-states"
    assert issuer.level == 1


def test_type_basic_invalid_numista_id_type() -> None:
    """Test TypeBasic validation with invalid numista_id type."""
    with pytest.raises(ValidationError):
        TypeBasic(  # type: ignore
            numista_id="invalid",
            title="Test",
            category="coin",
            issuer_code="test",
            issuer_name="Test",
        )


def test_type_basic_extra_field_forbidden() -> None:
    """Test extra fields are forbidden."""
    data = {
        "numista_id": 1,
        "title": "Test",
        "category": "coin",
        "issuer_code": "test",
        "issuer_name": "Test",
        "extra_field": "forbidden",
    }
    with pytest.raises(ValidationError):
        TypeBasic.model_validate(data)


def test_type_basic_title_max_length() -> None:
    """Test title max_length validation."""
    long_title = "a" * 501
    with pytest.raises(ValidationError):
        TypeBasic(  # type: ignore
            numista_id=1,
            title=long_title,
            category="coin",
            issuer_code="test",
            issuer_name="Test",
        )


def test_type_basic_to_dict() -> None:
    """Test TypeBasic to_dict method."""
    type_basic = TypeBasic(
        numista_id=95420,
        title="1 Thaler",
        category="coin",
        issuer_code="muhlhausen",
        issuer_name="Mühlhausen",
        min_year=1622,
        max_year=1622,
        obverse_thumbnail="https://example.com/obv.png",
        reverse_thumbnail="https://example.com/rev.png",
    )
    result = type_basic.to_dict()
    assert isinstance(result, dict)
    assert result["numista_id"] == TEST_NUMISTA_ID
    assert result["title"] == "1 Thaler"
    assert "max_year" not in result  # None excluded


def test_catalogue_missing_required() -> None:
    """Test Catalogue missing required fields."""
    with pytest.raises(ValidationError):
        Catalogue(  # type: ignore
            numista_id=1,
            title="Test",
        )


def test_catalogue_to_dict() -> None:
    """Test Catalogue to_dict method."""
    catalogue = Catalogue(
        numista_id=1,
        code="KM",
        title="Krause World Coins",
        author="Colin R. Bruce II",
        publisher="Krause Publications",
        isbn13="9781440248948",
    )
    result = catalogue.to_dict()
    assert isinstance(result, dict)
    assert result["code"] == "KM"
    assert "isbn13" not in result  # None excluded


def test_issuer_missing_required() -> None:
    """Test Issuer missing required fields."""
    with pytest.raises(ValidationError):
        Issuer(  # type: ignore
            name="United States",
            level=1,
        )


def test_issuer_to_dict() -> None:
    """Test Issuer to_dict method."""
    issuer = Issuer(
        code="united-states",
        name="United States",
        flag="https://example.com/flag.png",
        level=1,
        wikidata_id="Q30",
    )
    result = issuer.to_dict()
    assert isinstance(result, dict)
    assert result["code"] == "united-states"
    assert "parent_code" not in result  # None excluded


def test_type_full_invalid_weight_type() -> None:
    """Test TypeFull validation for invalid weight type."""
    with pytest.raises(ValidationError):
        TypeFull(  # type: ignore
            numista_id=1,
            title="Test",
            category="coin",
            issuer_code="test",
            issuer_name="Test",
            min_year=1622,
            max_year=1622,
            obverse_thumbnail="https://example.com/obverse.png",
            reverse_thumbnail="https://example.com/reverse.png",
            value_text="1",
            value_numeric=1.0,
            currency_name="Test",
            composition="Silver",
            diameter=42.0,
            thickness=2.5,
            obverse_description="",
            obverse_lettering="",
            reverse_description="",
            reverse_lettering="",
            weight="invalid",  # type: ignore
        )
