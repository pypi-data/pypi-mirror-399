"""Price service implementation."""

from collections.abc import Mapping
from typing import Any, cast

from numistalib import logger
from numistalib.client import AsyncClientProtocol, NumistaResponse, SyncClientProtocol
from numistalib.models.prices import Price
from numistalib.services.prices.base import PriceServiceBase


class PriceService(PriceServiceBase):
    """Unified price service supporting both sync and async clients."""

    CLASS_ITEMS_KEY = "prices"

    def __init__(self, client: SyncClientProtocol | AsyncClientProtocol) -> None:
        """Initialize price service.

        Parameters
        ----------
        client : SyncClientProtocol | AsyncClientProtocol
            HTTP client instance (sync or async)
        """
        super().__init__(client)

    def to_models(  # noqa: PLR6301
        self, items: list[Mapping[str, Any]], issue_id: int | None = None, **kwargs: Any  # noqa: ARG002
    ) -> list[Price]:
        """Convert API response to Price models.

        The API returns {currency: "EUR", prices: [{grade: "f", price: 180}]},
        so we need to extract the top-level currency and merge it with each price.

        Parameters
        ----------
        items : list[Mapping[str, Any]]
            Raw API response items (single dict with currency and prices array)
        issue_id : int | None
            Numista issue ID (required context)
        **kwargs : Any
            Additional conversion context

        Returns
        -------
        list[Price]
            Parsed price models
        """
        if issue_id is None:
            raise ValueError("issue_id is required for price conversion")

        # Items should be a list with one dict containing currency and prices
        if not items or len(items) == 0:
            return []

        # Extract currency from top-level response
        response_data = items[0] if isinstance(items, list) else items
        currency = cast(str, response_data.get("currency", "USD"))
        price_list = response_data.get("prices", [])

        prices: list[Price] = []
        for price_item in price_list:
            prices.append(
                Price(
                    issue_id=issue_id,
                    grade=cast(str, price_item["grade"]),
                    currency=currency,
                    value=cast(float, price_item["price"]),
                )
            )
        return prices

    def get_prices(
        self,
        type_id: int,
        issue_id: int,
        *,
        currency: str | None = None,
        lang: str | None = None,
    ) -> list[Price]:
        """Get price estimates for a specific issue.

        Supports both sync and async clients via duck-typing.

        Parameters
        ----------
        type_id : int
            Numista type ID
        issue_id : int
            Numista issue ID
        currency : str | None
            Filter by currency code
        lang : str | None
            Language code

        Returns
        -------
        list[Price]
            List of price estimates by grade

        Raises
        ------
        httpx.HTTPStatusError
            If issue not found or API error
        """
        logger.debug(
            "→ get_prices(type_id=%s, issue_id=%s, currency=%s, lang=%s)",
            type_id,
            issue_id,
            currency,
            lang,
        )

        params = self._build_params(currency=currency, lang=lang)

        response = cast(
            NumistaResponse,
            self._client.get(
                f"/types/{type_id}/issues/{issue_id}/prices", params=params
            ),
        )
        response.raise_for_status()
        self._track_response(response)

        items = self._extract_items_from_response(response)
        prices = self.to_models(items, issue_id=issue_id)

        logger.info(
            f"Retrieved {len(prices)} prices for issue {issue_id} {response.cached_indicator}"
        )
        return prices

    async def get_prices_async(
        self,
        type_id: int,
        issue_id: int,
        *,
        currency: str | None = None,
        lang: str | None = None,
    ) -> list[Price]:
        """Get price estimates for a specific issue (async).

        Parameters
        ----------
        type_id : int
            Numista type ID
        issue_id : int
            Numista issue ID
        currency : str | None
            Filter by currency code
        lang : str | None
            Language code

        Returns
        -------
        list[Price]
            List of price estimates by grade

        Raises
        ------
        httpx.HTTPStatusError
            If issue not found or API error
        """
        logger.debug(
            "→ get_prices_async(type_id=%s, issue_id=%s, currency=%s, lang=%s)",
            type_id,
            issue_id,
            currency,
            lang,
        )

        params = self._build_params(currency=currency, lang=lang)

        response = await self._aget(
            f"/types/{type_id}/issues/{issue_id}/prices", params=params
        )
        response.raise_for_status()
        self._track_response(response)

        items = self._extract_items_from_response(response)
        prices = self.to_models(items, issue_id=issue_id)

        logger.info(
            f"Retrieved {len(prices)} prices for issue {issue_id} {response.cached_indicator}"
        )
        return prices


# Backward compatibility exports
PriceServiceAsync = PriceService
