"""Issuer service implementation."""

from collections.abc import AsyncGenerator, Mapping
from typing import Any, cast

from numistalib import logger
from numistalib.client import AsyncClientProtocol, NumistaResponse, SyncClientProtocol
from numistalib.models.issuer import Issuer
from numistalib.services.issuer.base import IssuerServiceBase


class IssuerService(IssuerServiceBase):
    """Unified issuer service supporting both sync and async clients."""

    CLASS_ITEMS_KEY = "issuers"

    def __init__(self, client: SyncClientProtocol | AsyncClientProtocol) -> None:
        """Initialize issuer service.

        Parameters
        ----------
        client : SyncClientProtocol | AsyncClientProtocol
            HTTP client instance (sync or async)
        """
        super().__init__(client)

    def to_models(  # noqa: PLR6301
        self, items: list[Mapping[str, Any]], **kwargs: Any  # noqa: ARG002
    ) -> list[Issuer]:
        """Convert API response items to Issuer models.

        Parameters
        ----------
        items : list[Mapping[str, Any]]
            Raw API response items
        **kwargs : Any
            Unused (for interface consistency)

        Returns
        -------
        list[Issuer]
            Parsed issuer models
        """
        issuers: list[Issuer] = []
        for item in items:
            parent = cast(Mapping[str, Any] | None, item.get("parent"))
            issuers.append(
                Issuer(
                    code=cast(str, item["code"]),
                    name=cast(str, item["name"]),
                    flag=cast(str | None, item.get("flag")) or "",
                    wikidata_id=cast(str | None, item.get("wikidata_id")),
                    level=cast(int | None, item.get("level")) or 1,
                    parent_code=cast(str | None, parent.get("code")) if parent else None,
                    parent_name=cast(str | None, parent.get("name")) if parent else None,
                )
            )
        return issuers

    def get_issuers(self, lang: str = "en", count: int | None = None) -> list[Issuer]:
        """Get the list of issuers.

        Supports both sync and async clients via duck-typing.

        Parameters
        ----------
        lang : str
            Language code (en, es, fr)
        count : int | None
            Optional max results per page (API default is applied when None)

        Returns
        -------
        list[Issuer]
            List of issuers

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ get_issuers(lang=%s, count=%s)", lang, count)

        params = self._build_params({"lang": lang}, count=count)

        response = cast(NumistaResponse, self._client.get("/issuers", params=params))
        response.raise_for_status()
        self._track_response(response)

        items = self._extract_items_from_response(response)
        issuers = self.to_models(items)

        logger.info(f"Retrieved {len(issuers)} issuers {response.cached_indicator}")
        return issuers

    async def get_issuers_async(
        self, lang: str = "en", count: int | None = None
    ) -> list[Issuer]:
        """Get the list of issuers (async).

        Parameters
        ----------
        lang : str
            Language code (en, es, fr)
        count : int | None
            Optional max results per page (API default is applied when None)

        Returns
        -------
        list[Issuer]
            List of issuers

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ get_issuers_async(lang=%s, count=%s)", lang, count)

        params = self._build_params({"lang": lang}, count=count)

        response = await self._aget("/issuers", params=params)
        response.raise_for_status()
        self._track_response(response)

        items = self._extract_items_from_response(response)
        issuers = self.to_models(items)

        logger.info(f"Retrieved {len(issuers)} issuers {response.cached_indicator}")
        return issuers

    async def paginated_issuers(
        self,
        lang: str = "en",
        limit: int = 50,
    ) -> AsyncGenerator[Issuer]:
        """Lazily iterate all issuers by following pagination links.

        Parameters
        ----------
        lang : str
            Language code (en, es, fr)
        limit : int
            Results per page (max 100)

        Yields
        ------
        Issuer
            Individual issuer records
        """
        logger.debug("→ paginated_issuers(lang=%s, limit=%s)", lang, limit)

        url: str | None = f"/issuers?lang={lang}&count={limit}"
        page_count = 0

        while url:
            page_count += 1
            logger.debug("Fetching issuers page %s: %s", page_count, url)

            response = await self._aget(url)
            response.raise_for_status()
            self._track_response(response)

            data = cast(Mapping[str, Any], response.json())
            items = cast(list[Mapping[str, Any]], data.get(self.CLASS_ITEMS_KEY, []))
            issuers = self.to_models(items)

            for issuer in issuers:
                yield issuer

            url = cast(str | None, data.get("next_url"))

        logger.info("Finished paginating through %s pages of issuers", page_count)

    async def get_issuers_paginated(
        self,
        lang: str = "en",
        limit: int = 50,
    ) -> AsyncGenerator[Issuer]:
        """Paginate through all issuers (alias for paginated_issuers).

        Parameters
        ----------
        lang : str
            Language code (en, es, fr)
        limit : int
            Results per page (max 100)

        Yields
        ------
        Issuer
            Individual issuer records
        """
        async for issuer in self.paginated_issuers(lang=lang, limit=limit):
            yield issuer


# Backward compatibility exports
IssuerServiceAsync = IssuerService
