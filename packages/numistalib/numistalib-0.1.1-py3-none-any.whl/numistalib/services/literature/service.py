"""Literature service implementation."""

from collections.abc import Mapping
from typing import Any, cast

from numistalib import logger
from numistalib.client import AsyncClientProtocol, NumistaResponse, SyncClientProtocol
from numistalib.models import Publication
from numistalib.services.literature.base import LiteratureServiceBase


class LiteratureService(LiteratureServiceBase):
    """Unified literature service supporting both sync and async clients."""

    def __init__(self, client: SyncClientProtocol | AsyncClientProtocol) -> None:
        """Initialize literature service.

        Parameters
        ----------
        client : SyncClientProtocol | AsyncClientProtocol
            HTTP client instance (sync or async)
        """
        super().__init__(client)

    def to_models(  # noqa: PLR6301
        self, items: list[Mapping[str, Any]], **kwargs: Any  # noqa: ARG002
    ) -> list[Publication]:
        """Convert API response items to Publication models.

        Parameters
        ----------
        items : list[Mapping[str, Any]]
            Raw API response items
        **kwargs : Any
            Unused (for interface consistency)

        Returns
        -------
        list[Publication]
            Parsed publication models
        """
        return [Publication.model_validate(item) for item in items]

    def get_publication(self, publication_id: int) -> Publication:
        """Get publication details by ID.

        Parameters
        ----------
        publication_id : int
            Numista publication ID

        Returns
        -------
        Publication
            Publication details

        Examples
        --------
        >>> service = LiteratureService(client)
        >>> pub = service.get_publication(123)
        >>> print(pub.title)
        """
        logger.debug(f"Fetching publication {publication_id}")
        response = cast(NumistaResponse, self._client.get(f"/publications/{publication_id}"))
        response.raise_for_status()
        self._track_response(response)

        # Single publication, not wrapped in array
        data = cast(Mapping[str, Any], response.json())
        return self.to_models([data])[0]

    async def get_publication_async(self, publication_id: int) -> Publication:
        """Get publication details by ID (async).

        Parameters
        ----------
        publication_id : int
            Numista publication ID

        Returns
        -------
        Publication
            Publication details

        Examples
        --------
        >>> service = LiteratureService(async_client)
        >>> pub = await service.get_publication_async(123)
        >>> print(pub.title)
        """
        logger.debug(f"Fetching publication {publication_id} (async)")
        response = await self._aget(f"/publications/{publication_id}")
        response.raise_for_status()
        self._track_response(response)

        # Single publication, not wrapped in array
        data = cast(Mapping[str, Any], response.json())
        return self.to_models([data])[0]


__all__ = ["LiteratureService"]
