"""Image Search service implementation."""

from collections.abc import Mapping
from typing import Any, cast

from numistalib import logger
from numistalib.client import AsyncClientProtocol, NumistaResponse, SyncClientProtocol
from numistalib.models.types import TypeBasic
from numistalib.services.image_search.base import ImageSearchServiceBase


class ImageSearchService(ImageSearchServiceBase):
    """Unified image search service supporting both sync and async clients.

    This is a paid feature. See pricing page for details.
    """

    CLASS_ITEMS_KEY = "types"

    def __init__(self, client: SyncClientProtocol | AsyncClientProtocol) -> None:
        """Initialize image search service.

        Parameters
        ----------
        client : SyncClientProtocol | AsyncClientProtocol
            HTTP client instance (sync or async)
        """
        super().__init__(client)

    def to_models(  # noqa: PLR6301
        self, items: list[Mapping[str, Any]], **kwargs: Any  # noqa: ARG002
    ) -> list[TypeBasic]:
        """Convert API response items to TypeBasic models.

        Parameters
        ----------
        items : list[Mapping[str, Any]]
            Raw API response items
        **kwargs : Any
            Unused (for interface consistency)

        Returns
        -------
        list[TypeBasic]
            List of type models
        """
        return [TypeBasic.model_validate(item) for item in items]

    def search_by_image(
        self,
        images: list[dict[str, str]],
        category: str | None = None,
        lang: str = "en",
        activate_experimental_features: bool = False,
    ) -> list[TypeBasic]:
        """Search catalogue by image(s).

        This is a paid feature.

        Supports both sync and async clients via duck-typing.

        Parameters
        ----------
        images : list[dict]
            List of image objects with 'mime_type' and 'image_data' keys.
            Max 2 images. Max size 1024x1024 px.
        category : str | None
            Filter by category (coin, banknote, exonumia)
        lang : str
            Language code
        activate_experimental_features : bool
            Enable experimental features (beta, longer response time)

        Returns
        -------
        list[TypeBasic]
            List of matching types (up to 100)

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        ValueError
            If invalid image count or size
        """
        logger.debug(
            "→ search_by_image(image_count=%s, category=%s, lang=%s, experimental=%s)",
            len(images),
            category,
            lang,
            activate_experimental_features,
        )

        params = self._build_params(
            lang=lang,
            activate_experimental_features=activate_experimental_features or None,
        )

        payload: dict[str, object] = {"images": images}
        if category:
            payload["category"] = category

        response = cast(
            NumistaResponse,
            self._client.post("/search_by_image", params=params, json=payload),
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())
        items = cast(list[Mapping[str, Any]], data.get(self.CLASS_ITEMS_KEY, []))

        types = self.to_models(items)

        logger.info(
            f"Image search found {len(types)} matching types {response.cached_indicator}"
        )
        return types

    async def search_by_image_async(
        self,
        images: list[dict[str, str]],
        category: str | None = None,
        lang: str = "en",
        activate_experimental_features: bool = False,
    ) -> list[TypeBasic]:
        """Search catalogue by image(s) (async).

        This is a paid feature.

        Parameters
        ----------
        images : list[dict]
            List of image objects with 'mime_type' and 'image_data' keys.
            Max 2 images. Max size 1024x1024 px.
        category : str | None
            Filter by category (coin, banknote, exonumia)
        lang : str
            Language code
        activate_experimental_features : bool
            Enable experimental features (beta, longer response time)

        Returns
        -------
        list[TypeBasic]
            List of matching types (up to 100)

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        ValueError
            If invalid image count or size
        """
        logger.debug(
            "→ search_by_image_async(image_count=%s, category=%s, lang=%s, experimental=%s)",
            len(images),
            category,
            lang,
            activate_experimental_features,
        )

        params = self._build_params(
            lang=lang,
            activate_experimental_features=activate_experimental_features or None,
        )

        payload: dict[str, object] = {"images": images}
        if category:
            payload["category"] = category

        response = await self._apost("/search_by_image", params=params, json=payload)
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())
        items = cast(list[Mapping[str, Any]], data.get(self.CLASS_ITEMS_KEY, []))

        types = self.to_models(items)

        logger.info(
            f"Image search found {len(types)} matching types {response.cached_indicator}"
        )
        return types


# Backward compatibility exports
ImageSearchServiceAsync = ImageSearchService
