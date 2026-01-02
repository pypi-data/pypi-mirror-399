"""Catalogue service implementation."""

from collections.abc import Mapping
from typing import Any, cast

from numistalib import logger
from numistalib.client import AsyncClientProtocol, NumistaResponse, SyncClientProtocol
from numistalib.models.catalogues import Catalogue
from numistalib.services.catalogues.base import CatalogueServiceBase


class CatalogueService(CatalogueServiceBase):
    """Unified catalogue service supporting both sync and async clients."""

    CLASS_ITEMS_KEY = "catalogues"

    def __init__(self, client: SyncClientProtocol | AsyncClientProtocol) -> None:
        """Initialize catalogue service.

        Parameters
        ----------
        client : SyncClientProtocol | AsyncClientProtocol
            HTTP client instance (sync or async)
        """
        super().__init__(client)

    def to_models(  # noqa: PLR6301
        self, items: list[Mapping[str, Any]], **kwargs: Any  # noqa: ARG002
    ) -> list[Catalogue]:
        """Convert API response items to Catalogue models.

        Parameters
        ----------
        items : list[Mapping[str, Any]]
            Raw API response items
        **kwargs : Any
            Unused (for interface consistency)

        Returns
        -------
        list[Catalogue]
            Parsed catalogue models
        """
        catalogues: list[Catalogue] = []
        for item in items:
            catalogues.append(
                Catalogue(
                    id=cast(int, item["id"]),
                    code=cast(str, item["code"]),
                    title=cast(str, item["title"]),
                    author=cast(str | None, item.get("author")),
                    publisher=cast(str | None, item.get("publisher")),
                    isbn13=cast(str | None, item.get("isbn13")),
                )
            )
        return catalogues

    def get_catalogues(self) -> list[Catalogue]:
        """Get list of all reference catalogues.

        Supports both sync and async clients via duck-typing.

        Returns
        -------
        list[Catalogue]
            All available catalogues

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ get_catalogues()")

        response = cast(NumistaResponse, self._client.get("/catalogues"))
        response.raise_for_status()
        self._track_response(response)
        self._track_response(response)

        items = self._extract_items_from_response(response)
        catalogues = self.to_models(items)

        logger.info(f"Retrieved {len(catalogues)} catalogues {response.cached_indicator}")
        return catalogues

    async def get_catalogues_async(self) -> list[Catalogue]:
        """Get list of all reference catalogues (async).

        Returns
        -------
        list[Catalogue]
            All available catalogues

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ get_catalogues_async()")

        response = await self._aget("/catalogues")
        response.raise_for_status()
        self._track_response(response)

        items = self._extract_items_from_response(response)
        catalogues = self.to_models(items)

        logger.info(f"Retrieved {len(catalogues)} catalogues {response.cached_indicator}")
        return catalogues


# Backward compatibility exports
CatalogueServiceAsync = CatalogueService
