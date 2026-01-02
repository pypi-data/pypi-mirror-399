"""Mint service implementation."""

from collections.abc import Mapping
from typing import Any, cast

from numistalib import logger
from numistalib.client import AsyncClientProtocol, NumistaResponse, SyncClientProtocol
from numistalib.models.mints import Mint
from numistalib.services.mints.base import MintServiceBase


class MintService(MintServiceBase):
    """Unified mint service supporting both sync and async clients."""

    CLASS_ITEMS_KEY = "mints"

    def __init__(self, client: SyncClientProtocol | AsyncClientProtocol) -> None:
        """Initialize mint service.

        Parameters
        ----------
        client : SyncClientProtocol | AsyncClientProtocol
            HTTP client instance (sync or async)
        """
        super().__init__(client)

    def to_models(  # noqa: PLR6301
        self, items: list[Mapping[str, Any]], **kwargs: Any  # noqa: ARG002
    ) -> list[Mint]:
        """Convert API response items to Mint models.

        Parameters
        ----------
        items : list[Mapping[str, Any]]
            Raw API response items
        **kwargs : Any
            Unused (for interface consistency)

        Returns
        -------
        list[Mint]
            Parsed mint models
        """
        return [Mint.model_validate(item) for item in items]

    def get_mints(self, lang: str = "en") -> list[Mint]:
        """Get list of all mints.

        Supports both sync and async clients via duck-typing.

        Parameters
        ----------
        lang : str
            Language code (en, es, fr)

        Returns
        -------
        list[Mint]
            List of all mints

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ get_mints(lang=%s)", lang)

        response = cast(
            NumistaResponse, self._client.get("/mints", params={"lang": lang})
        )
        response.raise_for_status()
        self._track_response(response)

        items = self._extract_items_from_response(response)
        mints = self.to_models(items)

        logger.info(f"Retrieved {len(mints)} mints {response.cached_indicator}")
        return mints

    def get_mint(self, mint_id: int, *, lang: str | None = None) -> Mint:
        """Get details about a specific mint.

        Parameters
        ----------
        mint_id : int
            Numista mint ID

        Returns
        -------
        Mint
            Mint details

        Raises
        ------
        httpx.HTTPStatusError
            If mint not found or API error
        """
        logger.debug("→ get_mint(mint_id=%s, lang=%s)", mint_id, lang)

        params = {"lang": lang} if lang else None
        response = cast(NumistaResponse, self._client.get(f"/mints/{mint_id}", params=params))
        response.raise_for_status()
        self._track_response(response)

        data = cast(Mapping[str, Any], response.json())
        mint = self.to_models([data])[0]

        logger.info(f"Retrieved mint {mint_id}: {mint.name} {response.cached_indicator}")
        return mint

    async def get_mints_async(self, lang: str = "en") -> list[Mint]:
        """Get list of all mints (async).

        Parameters
        ----------
        lang : str
            Language code (en, es, fr)

        Returns
        -------
        list[Mint]
            List of all mints

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ get_mints_async(lang=%s)", lang)

        response = await self._aget("/mints", params={"lang": lang})
        response.raise_for_status()
        self._track_response(response)

        items = self._extract_items_from_response(response)
        mints = self.to_models(items)

        logger.info(f"Retrieved {len(mints)} mints {response.cached_indicator}")
        return mints

    async def get_mint_async(self, mint_id: int, *, lang: str | None = None) -> Mint:
        """Get details about a specific mint (async).

        Parameters
        ----------
        mint_id : int
            Numista mint ID

        Returns
        -------
        Mint
            Mint details

        Raises
        ------
        httpx.HTTPStatusError
            If mint not found or API error
        """
        logger.debug("→ get_mint_async(mint_id=%s, lang=%s)", mint_id, lang)

        params = {"lang": lang} if lang else None
        response = await self._aget(f"/mints/{mint_id}", params=params)
        response.raise_for_status()
        self._track_response(response)

        data = cast(Mapping[str, Any], response.json())
        mint = self.to_models([data])[0]

        logger.info(f"Retrieved mint {mint_id}: {mint.name} {response.cached_indicator}")
        return mint


# Backward compatibility exports
MintServiceAsync = MintService
