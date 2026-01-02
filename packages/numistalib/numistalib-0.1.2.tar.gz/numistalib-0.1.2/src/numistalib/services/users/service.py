"""User service implementation."""

from collections.abc import Mapping
from typing import Any, cast

from numistalib import logger
from numistalib.client import AsyncClientProtocol, NumistaResponse, SyncClientProtocol
from numistalib.models.collections import CollectedItem
from numistalib.models.users import User
from numistalib.services.users.base import UserServiceBase


class UserService(UserServiceBase):
    """Unified user service supporting both sync and async clients."""

    def __init__(self, client: SyncClientProtocol | AsyncClientProtocol) -> None:
        """Initialize user service.

        Parameters
        ----------
        client : SyncClientProtocol | AsyncClientProtocol
            HTTP client instance (sync or async)
        """
        super().__init__(client)

    def to_models(  # noqa: PLR6301
        self, items: list[Mapping[str, Any]], **kwargs: Any  # noqa: ARG002
    ) -> list[User]:
        """Convert API response items to User models.

        Parameters
        ----------
        items : list[Mapping[str, Any]]
            Raw API response items (single item)
        **kwargs : Any
            Unused (for interface consistency)

        Returns
        -------
        list[User]
            List with single User model
        """
        return [User.model_validate(item) for item in items]

    def get_user(self, user_id: int) -> User:
        """Get details about a specific user.

        Supports both sync and async clients via duck-typing.

        Parameters
        ----------
        user_id : int
            Numista user ID

        Returns
        -------
        User
            User profile details

        Raises
        ------
        httpx.HTTPStatusError
            If user not found or API error
        """
        logger.debug("→ get_user(user_id=%s)", user_id)

        response = cast(NumistaResponse, self._client.get(f"/users/{user_id}"))
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        user = self.to_models([data.get("user", {})])[0]

        logger.info(f"Retrieved user {user_id}: {user.username} {response.cached_indicator}")
        return user

    def get_collections(self, user_id: int) -> list[dict[str, Any]]:
        """Get list of collections for a user.

        Parameters
        ----------
        user_id : int
            Numista user ID

        Returns
        -------
        list[dict[str, Any]]
            List of collection objects

        Raises
        ------
        httpx.HTTPStatusError
            If user not found or API error
        """
        logger.debug("→ get_collections(user_id=%s)", user_id)

        response = cast(NumistaResponse, self._client.get(f"/users/{user_id}/collections"))
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        collections: list[dict[str, Any]] = data.get("collections", [])

        logger.info(
            f"Retrieved {len(collections)} collections for user {user_id} {response.cached_indicator}"
        )
        return collections

    def get_collected_items(
        self,
        user_id: int,
        category: str | None = None,
        type_id: int | None = None,
        collection_id: int | None = None,
    ) -> list[CollectedItem]:
        """Get collected items for a user.

        Parameters
        ----------
        user_id : int
            Numista user ID
        category : str | None
            Filter by category (coin, banknote, exonumia)
        type_id : int | None
            Filter by type ID
        collection_id : int | None
            Filter by collection ID

        Returns
        -------
        list[CollectedItem]
            List of collected items

        Raises
        ------
        httpx.HTTPStatusError
            If user not found or API error
        """
        logger.debug(
            "→ get_collected_items(user_id=%s, category=%s, type_id=%s, collection_id=%s)",
            user_id,
            category,
            type_id,
            collection_id,
        )

        params = self._build_params(
            category=category, type=type_id, collection=collection_id
        )

        response = cast(
            NumistaResponse,
            self._client.get(f"/users/{user_id}/collected_items", params=params),
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        items_list = [
            CollectedItem.model_validate(item)
            for item in data.get("collected_items", [])
        ]

        logger.info(
            f"Retrieved {len(items_list)} collected items for user {user_id} {response.cached_indicator}"
        )
        return items_list

    async def get_user_async(self, user_id: int) -> User:
        """Get details about a specific user (async).

        Parameters
        ----------
        user_id : int
            Numista user ID

        Returns
        -------
        User
            User profile details

        Raises
        ------
        httpx.HTTPStatusError
            If user not found or API error
        """
        logger.debug("→ get_user_async(user_id=%s)", user_id)

        response = await cast(AsyncClientProtocol, self._client).get(f"/users/{user_id}")
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        user = self.to_models([data.get("user", {})])[0]

        logger.info(f"Retrieved user {user_id}: {user.username} {response.cached_indicator}")
        return user

    async def get_collections_async(self, user_id: int) -> list[dict[str, Any]]:
        """Get list of collections for a user (async).

        Parameters
        ----------
        user_id : int
            Numista user ID

        Returns
        -------
        list[dict[str, Any]]
            List of collection objects

        Raises
        ------
        httpx.HTTPStatusError
            If user not found or API error
        """
        logger.debug("→ get_collections_async(user_id=%s)", user_id)

        response = await cast(AsyncClientProtocol, self._client).get(f"/users/{user_id}/collections")
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        collections: list[dict[str, Any]] = data.get("collections", [])

        logger.info(
            f"Retrieved {len(collections)} collections for user {user_id} {response.cached_indicator}"
        )
        return collections

    async def get_collected_items_async(
        self,
        user_id: int,
        category: str | None = None,
        type_id: int | None = None,
        collection_id: int | None = None,
    ) -> list[CollectedItem]:
        """Get collected items for a user (async).

        Parameters
        ----------
        user_id : int
            Numista user ID
        category : str | None
            Filter by category (coin, banknote, exonumia)
        type_id : int | None
            Filter by type ID
        collection_id : int | None
            Filter by collection ID

        Returns
        -------
        list[CollectedItem]
            List of collected items

        Raises
        ------
        httpx.HTTPStatusError
            If user not found or API error
        """
        logger.debug(
            "→ get_collected_items_async(user_id=%s, category=%s, type_id=%s, collection_id=%s)",
            user_id,
            category,
            type_id,
            collection_id,
        )

        params = self._build_params(
            category=category, type=type_id, collection=collection_id
        )

        response = await cast(AsyncClientProtocol, self._client).get(f"/users/{user_id}/collected_items", params=params)
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        items_list = [
            CollectedItem.model_validate(item)
            for item in data.get("collected_items", [])
        ]

        logger.info(
            f"Retrieved {len(items_list)} collected items for user {user_id} {response.cached_indicator}"
        )
        return items_list


# Backward compatibility exports
UserServiceAsync = UserService
