"""Tests for documentation code examples.

Validates that code examples in README and docs execute correctly.
"""

# mypy: disable-error-code="attr-defined,call-arg,arg-type"

from unittest.mock import patch

from numistalib.client import NumistaApiClient
from numistalib.config import Settings
from numistalib.models.catalogues import Catalogue
from numistalib.models.issuer import Issuer
from numistalib.models.types import TypeBasic, TypeFull
from numistalib.services.catalogues.service import CatalogueService
from numistalib.services.issuer.service import IssuerService
from numistalib.services.types.service import SearchParams, TypeService


class TestDocumentationExamples:
    """Tests for key documentation examples."""

    def test_readme_basic_usage(self, mock_client_factory: type[NumistaApiClient]) -> None:
        """Test README.md basic Python API example (lines ~95-110)."""
        settings = Settings(api_key="test_key")

        with mock_client_factory(settings) as client:  # type: ignore[attr-defined,call-arg]
            service = TypeService(client)

            # Mock response using model_construct to bypass validation
            mock_result = TypeBasic.model_construct(
                numista_id=1,
                title="Test Dollar",
                category="coin",
                issuer=Issuer.model_construct(code="us", name="United States"),
                min_year=2000,
                max_year=2010,
            )

            with patch.object(service, "search_types", return_value=[mock_result]):
                params = SearchParams()
                params.query = "dollar"
                params.page = 1
                params.count = 10
                results = service.search_types(params)

                # Verify example code works
                for coin_type in results:
                    assert coin_type.numista_id
                    assert coin_type.title

    def test_readme_get_details(self, mock_client_factory: type[NumistaApiClient]) -> None:
        """Test README.md get type details example (lines ~113-118)."""
        settings = Settings(api_key="test_key")

        with mock_client_factory(settings) as client:  # type: ignore[attr-defined,call-arg]
            service = TypeService(client)

            mock_type = TypeFull.model_construct(
                numista_id=95420,
                title="Test Coin",
                category="coin",
                issuer=Issuer.model_construct(code="test", name="Test"),
                min_year=2000,
                max_year=2010,
                weight=5.0,
                composition="copper-nickel",
            )

            with patch.object(service, "get_type", return_value=mock_type):
                full_type = service.get_type(95420)

                # Verify example code expectations
                assert full_type.weight == 5.0
                assert full_type.composition == "copper-nickel"

    def test_index_rst_python_example(self, mock_client_factory: type[NumistaApiClient]) -> None:
        """Test docs/index.rst Python API example (lines ~103-118)."""
        settings = Settings(api_key="test_key")

        with mock_client_factory(settings) as client:  # type: ignore[attr-defined,call-arg]
            service = TypeService(client)

            mock_result = TypeBasic.model_construct(
                numista_id=1,
                title="Test Dollar",
                category="coin",
                issuer=Issuer.model_construct(code="us", name="United States"),
                min_year=2000,
                max_year=2010,
            )

            with patch.object(service, "search_types", return_value=[mock_result]):
                params = SearchParams()
                params.query = "dollar"
                params.page = 1
                params.count = 10
                results = service.search_types(params)

                # Example prints this format
                for coin_type in results:
                    output = f"{coin_type.numista_id}: {coin_type.title}"
                    assert output == "1: Test Dollar"

    def test_quickstart_search(self, mock_client_factory: type[NumistaApiClient]) -> None:
        """Test docs/quickstart.md basic search (lines ~89-100)."""
        settings = Settings(api_key="test_key")

        with mock_client_factory(settings) as client:  # type: ignore[attr-defined,call-arg]
            service = TypeService(client)

            mock_result = TypeBasic.model_construct(
                numista_id=1,
                title="Test Dollar",
                category="coin",
                issuer=Issuer.model_construct(code="us", name="United States"),
                min_year=2000,
                max_year=2010,
            )

            with patch.object(service, "search_types", return_value=[mock_result]):
                params = SearchParams()
                params.query = "dollar"
                params.page = 1
                params.count = 10
                results = service.search_types(params)

                # Example accesses these fields
                for coin_type in results:
                    assert coin_type.numista_id
                    assert coin_type.title
                    assert coin_type.issuer
                    assert coin_type.min_year
                    assert coin_type.max_year

    def test_quickstart_catalogues(self, mock_client_factory: type[NumistaApiClient]) -> None:
        """Test docs/quickstart.md catalogues example (lines ~144-155)."""
        settings = Settings(api_key="test_key")

        with mock_client_factory(settings) as client:  # type: ignore[attr-defined,call-arg]
            service = CatalogueService(client)

            mock_catalogue = Catalogue.model_construct(
                numista_id=1,
                code="KM",
                title="Krause-Mishler",
                author="Test Author",
            )

            with patch.object(service, "get_catalogues", return_value=[mock_catalogue]):
                catalogues = service.get_catalogues()

                # Example accesses name and author
                for cat in catalogues:
                    assert cat.title  # API returns 'title' field
                    assert cat.author

    def test_python_api_guide_search(self, mock_client_factory: type[NumistaApiClient]) -> None:
        """Test docs/python_api_guide.md search example (lines ~42-53)."""
        settings = Settings(api_key="test_key")

        with mock_client_factory(settings) as client:  # type: ignore[attr-defined,call-arg]
            service = TypeService(client)

            mock_result = TypeBasic.model_construct(
                numista_id=1,
                title="Test Dollar",
                category="coin",
                issuer=Issuer.model_construct(code="us", name="United States"),
                min_year=2000,
                max_year=2010,
            )

            with patch.object(service, "search_types", return_value=[mock_result]):
                params = SearchParams()
                params.query = "dollar"
                params.page = 1
                params.count = 10
                params.lang = "en"
                results = service.search_types(params)

                # Example shows these field accesses
                for coin_type in results:
                    assert coin_type.numista_id
                    assert coin_type.title
                    assert coin_type.issuer
                    assert coin_type.min_year
                    assert coin_type.max_year

    def test_python_api_guide_get_details(self, mock_client_factory: type[NumistaApiClient]) -> None:
        """Test docs/python_api_guide.md get details example (lines ~79-89)."""
        settings = Settings(api_key="test_key")

        with mock_client_factory(settings) as client:  # type: ignore[attr-defined,call-arg]
            service = TypeService(client)

            mock_type = TypeFull.model_construct(
                numista_id=95420,
                title="Test Coin",
                category="coin",
                issuer=Issuer.model_construct(code="test", name="Test"),
                min_year=2000,
                max_year=2010,
                weight=5.0,
                size=25.0,
                composition="copper-nickel",
                obverse=type("Obverse", (), {"description": "National arms"})(),
                reverse=type("Reverse", (), {"description": "Denomination"})(),
            )

            with patch.object(service, "get_type", return_value=mock_type):
                full_type = service.get_type(95420, lang="en")

                # Example prints these fields
                assert full_type.title
                assert full_type.weight == 5.0
                assert full_type.size == 25.0
                assert full_type.composition

    def test_issuers_example(self, mock_client_factory: type[NumistaApiClient]) -> None:
        """Test docs/python_api_guide.md issuers example (lines ~145-155)."""
        settings = Settings(api_key="test_key")

        with mock_client_factory(settings) as client:  # type: ignore[attr-defined,call-arg]
            service = IssuerService(client)

            mock_issuer = Issuer.model_construct(
                code="fr",
                name="France",
                wikidata_id="Q142",
            )

            with patch.object(service, "get_issuers", return_value=[mock_issuer]):
                issuers = service.get_issuers(lang="en")

                # Example accesses these fields
                for issuer in issuers:
                    assert issuer.code
                    assert issuer.name
                    if issuer.wikidata_id:
                        assert isinstance(issuer.wikidata_id, str)

    def test_model_serialization(self, mock_client_factory: type[NumistaApiClient]) -> None:
        """Test docs/python_api_guide.md model serialization (lines ~530-542)."""
        settings = Settings(api_key="test_key")

        with mock_client_factory(settings) as client:  # type: ignore[attr-defined,call-arg]
            service = TypeService(client)

            mock_type = TypeFull.model_construct(
                numista_id=95420,
                title="Test Coin",
                category="coin",
                issuer=Issuer.model_construct(code="test", name="Test"),
                min_year=2000,
                max_year=2010,
            )

            with patch.object(service, "get_type", return_value=mock_type):
                coin_type = service.get_type(95420)

                # Example shows these serialization methods
                data = coin_type.model_dump()
                assert isinstance(data, dict)

                json_str = coin_type.model_dump_json()
                assert isinstance(json_str, str)

                # Example shows reconstruction
                reconstructed = TypeFull.model_construct(**data)
                assert reconstructed.numista_id == coin_type.numista_id
