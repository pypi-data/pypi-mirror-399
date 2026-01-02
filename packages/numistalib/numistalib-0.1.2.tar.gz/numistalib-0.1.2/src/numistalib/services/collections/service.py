"""Collection service implementation."""

from collections.abc import Mapping
from typing import Any, cast

from numistalib import logger
from numistalib.client import AsyncClientProtocol, NumistaResponse, SyncClientProtocol
from numistalib.models.collections import CollectedItem, GradingDetails, Picture, TypeDetail, UserCollection
from numistalib.services.collections.base import CollectionServiceBase


class CollectionService(CollectionServiceBase):
    """Unified collection service supporting both sync and async clients.

    Requires OAuth authentication with appropriate scopes.
    """

    def __init__(self, client: SyncClientProtocol | AsyncClientProtocol) -> None:
        """Initialize collection service.

        Parameters
        ----------
        client : SyncClientProtocol | AsyncClientProtocol
            HTTP client instance (sync or async)
        """
        super().__init__(client)

    def to_models(  # noqa: PLR6301
        self, items: list[Mapping[str, Any]], user_id: int | None = None, **kwargs: Any  # noqa: ARG002
    ) -> list[CollectedItem]:
        """Convert API response items to CollectedItem models.

        Parameters
        ----------
        items : list[Mapping[str, Any]]
            Raw API response items
        user_id : int | None
            Associated user ID (not used, kept for interface compatibility)
        **kwargs : Any
            Additional context

        Returns
        -------
        list[CollectedItem]
            Parsed collected item models
        """
        collected_items: list[CollectedItem] = []
        for item in items:
            type_dict = cast(Mapping[str, Any], item["type"])
            type_obj = TypeDetail(**type_dict)

            issue_obj = None
            if item.get("issue"):
                issue_obj = cast(dict[str, object], item["issue"])

            price_obj = None
            if item.get("price"):
                price_obj = cast(dict[str, object], item["price"])

            collection_obj = None
            if item.get("collection"):
                collection_dict = cast(Mapping[str, Any], item["collection"])
                collection_obj = UserCollection(**collection_dict)

            pictures_obj = None
            if item.get("pictures"):
                pictures_list = cast(list[Mapping[str, Any]], item["pictures"])
                pictures_obj = [Picture(**pic) for pic in pictures_list]

            grading_obj = None
            if item.get("grading_details"):
                grading_dict = cast(Mapping[str, Any], item["grading_details"])
                grading_obj = GradingDetails(**grading_dict)

            grade_val = cast(str | None, item.get("grade"))

            collected_items.append(
                CollectedItem(
                    id=cast(int, item["id"]),
                    quantity=cast(int, item.get("quantity", 1)),
                    type=type_obj,
                    for_swap=bool(item.get("for_swap", False)),
                    issue=issue_obj,
                    grade=grade_val,  # type: ignore[arg-type]
                    private_comment=cast(str | None, item.get("private_comment")),
                    public_comment=cast(str | None, item.get("public_comment")),
                    price=price_obj,
                    collection=collection_obj,
                    pictures=pictures_obj,
                    storage_location=cast(str | None, item.get("storage_location")),
                    acquisition_place=cast(str | None, item.get("acquisition_place")),
                    acquisition_date=cast(Any, item.get("acquisition_date")),  # type: ignore[arg-type]
                    serial_number=cast(str | None, item.get("serial_number")),
                    internal_id=cast(str | None, item.get("internal_id")),
                    weight=cast(float | None, item.get("weight")),
                    size=cast(float | None, item.get("size")),
                    axis=cast(int | None, item.get("axis")),
                    grading_details=grading_obj,
                )
            )
        return collected_items

    def get_collected_items(
        self,
        user_id: int,
        category: str | None = None,
        type_id: int | None = None,
        collection_id: int | None = None,
    ) -> list[CollectedItem]:
        """Get all items in a user's collection.

        Requires OAuth 2.0 authentication with 'view_collection' scope.
        Supports both sync and async clients via duck-typing.

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
            If user not found, unauthorized, or API error
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
        items_raw = cast(list[Mapping[str, Any]], data.get("collected_items", []))

        items = self.to_models(items_raw, user_id=user_id)

        logger.info(
            f"Retrieved {len(items)} collected items for user {user_id} {response.cached_indicator}"
        )
        return items

    def get_collected_item(self, user_id: int, item_id: int) -> CollectedItem:
        """Get details about a specific collected item.

        Requires OAuth 2.0 authentication with 'view_collection' scope.

        Parameters
        ----------
        user_id : int
            Numista user ID
        item_id : int
            Collected item ID

        Returns
        -------
        CollectedItem
            Collected item details

        Raises
        ------
        httpx.HTTPStatusError
            If item not found, unauthorized, or API error
        """
        logger.debug(
            "→ get_collected_item(user_id=%s, item_id=%s)",
            user_id,
            item_id,
        )

        response = cast(
            NumistaResponse,
            self._client.get(f"/users/{user_id}/collected_items/{item_id}"),
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        item = self.to_models([data], user_id=user_id)[0]

        logger.info(f"Retrieved collected item {item_id} {response.cached_indicator}")
        return item

    def get_collections(self, user_id: int) -> list[UserCollection]:
        """Get all collections for a user.

        Requires OAuth 2.0 authentication with 'view_collection' scope.

        Parameters
        ----------
        user_id : int
            Numista user ID

        Returns
        -------
        list[UserCollection]
            List of user collections

        Raises
        ------
        httpx.HTTPStatusError
            If user not found, unauthorized, or API error
        """
        logger.debug("→ get_collections(user_id=%s)", user_id)

        response = cast(
            NumistaResponse,
            self._client.get(f"/users/{user_id}/collections"),
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())
        collections_raw = cast(list[Mapping[str, Any]], data.get("collections", []))

        collections = [
            UserCollection(
                numista_id=cast(int, col["id"]),
                name=cast(str, col["name"]),
            )
            for col in collections_raw
        ]

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
        """Get all items in a user's collection (async).

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
            If user not found, unauthorized, or API error
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

        response = await self._aget(f"/users/{user_id}/collected_items", params=params)
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())
        items_raw = cast(list[Mapping[str, Any]], data.get("collected_items", []))

        items = self.to_models(items_raw, user_id=user_id)

        logger.info(
            f"Retrieved {len(items)} collected items for user {user_id} {response.cached_indicator}"
        )
        return items

    async def get_collected_item_async(self, user_id: int, item_id: int) -> CollectedItem:
        """Get details about a specific collected item (async).

        Parameters
        ----------
        user_id : int
            Numista user ID
        item_id : int
            Collected item ID

        Returns
        -------
        CollectedItem
            Collected item details

        Raises
        ------
        httpx.HTTPStatusError
            If item not found, unauthorized, or API error
        """
        logger.debug(
            "→ get_collected_item_async(user_id=%s, item_id=%s)",
            user_id,
            item_id,
        )

        response = await self._aget(f"/users/{user_id}/collected_items/{item_id}")
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        item = self.to_models([data], user_id=user_id)[0]

        logger.info(f"Retrieved collected item {item_id} {response.cached_indicator}")
        return item

    async def get_collections_async(self, user_id: int) -> list[UserCollection]:
        """Get all collections for a user (async).

        Parameters
        ----------
        user_id : int
            Numista user ID

        Returns
        -------
        list[UserCollection]
            List of user collections

        Raises
        ------
        httpx.HTTPStatusError
            If user not found, unauthorized, or API error
        """
        logger.debug("→ get_collections_async(user_id=%s)", user_id)

        response = await self._aget(f"/users/{user_id}/collections")
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())
        collections_raw = cast(list[Mapping[str, Any]], data.get("collections", []))

        collections = [
            UserCollection(
                numista_id=cast(int, col["id"]),
                name=cast(str, col["name"]),
            )
            for col in collections_raw
        ]

        logger.info(
            f"Retrieved {len(collections)} collections for user {user_id} {response.cached_indicator}"
        )
        return collections

    def add_collected_item(self, user_id: int, item_data: dict[str, object]) -> CollectedItem:
        """Add item to user's collection.

        Requires OAuth 2.0 authentication with 'edit_collection' scope.

        Parameters
        ----------
        user_id : int
            Numista user ID
        item_data : dict
            Item data payload

        Returns
        -------
        CollectedItem
            Created collected item

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ add_collected_item(user_id=%s)", user_id)

        response = cast(
            NumistaResponse,
            self._client.post(f"/users/{user_id}/collected_items", json=item_data),
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        item = self.to_models([data], user_id=user_id)[0]

        logger.info(f"Added collected item {item.id} {response.cached_indicator}")
        return item

    async def add_collected_item_async(self, user_id: int, item_data: dict[str, object]) -> CollectedItem:
        """Add item to user's collection (async).

        Requires OAuth 2.0 authentication with 'edit_collection' scope.

        Parameters
        ----------
        user_id : int
            Numista user ID
        item_data : dict
            Item data payload

        Returns
        -------
        CollectedItem
            Created collected item

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ add_collected_item_async(user_id=%s)", user_id)

        response = await self._apost(f"/users/{user_id}/collected_items", json=item_data)
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        item = self.to_models([data], user_id=user_id)[0]

        logger.info(f"Added collected item {item.id} {response.cached_indicator}")
        return item

    def edit_collected_item(self, user_id: int, item_id: int, item_data: dict[str, object]) -> CollectedItem:
        """Edit item in user's collection.

        Requires OAuth 2.0 authentication with 'edit_collection' scope.

        Parameters
        ----------
        user_id : int
            Numista user ID
        item_id : int
            Collected item ID
        item_data : dict
            Item data payload (all fields optional)

        Returns
        -------
        CollectedItem
            Updated collected item

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ edit_collected_item(user_id=%s, item_id=%s)", user_id, item_id)

        response = cast(
            NumistaResponse,
            self._client.patch(
                f"/users/{user_id}/collected_items/{item_id}", json=item_data
            ),
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        item = self.to_models([data], user_id=user_id)[0]

        logger.info(f"Edited collected item {item_id} {response.cached_indicator}")
        return item

    async def edit_collected_item_async(
        self, user_id: int, item_id: int, item_data: dict[str, object]
    ) -> CollectedItem:
        """Edit item in user's collection (async).

        Requires OAuth 2.0 authentication with 'edit_collection' scope.

        Parameters
        ----------
        user_id : int
            Numista user ID
        item_id : int
            Collected item ID
        item_data : dict
            Item data payload (all fields optional)

        Returns
        -------
        CollectedItem
            Updated collected item

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ edit_collected_item_async(user_id=%s, item_id=%s)", user_id, item_id)

        response = await self._apatch(
            f"/users/{user_id}/collected_items/{item_id}", json=item_data
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        item = self.to_models([data], user_id=user_id)[0]

        logger.info(f"Edited collected item {item_id} {response.cached_indicator}")
        return item

    def delete_collected_item(self, user_id: int, item_id: int) -> None:
        """Delete item from user's collection.

        Requires OAuth 2.0 authentication with 'edit_collection' scope.

        Parameters
        ----------
        user_id : int
            Numista user ID
        item_id : int
            Collected item ID

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ delete_collected_item(user_id=%s, item_id=%s)", user_id, item_id)

        response = cast(
            NumistaResponse,
            self._client.delete(f"/users/{user_id}/collected_items/{item_id}"),
        )
        response.raise_for_status()
        self._track_response(response)

        logger.info(f"Deleted collected item {item_id} {response.cached_indicator}")

    async def delete_collected_item_async(self, user_id: int, item_id: int) -> None:
        """Delete item from user's collection (async).

        Requires OAuth 2.0 authentication with 'edit_collection' scope.

        Parameters
        ----------
        user_id : int
            Numista user ID
        item_id : int
            Collected item ID

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ delete_collected_item_async(user_id=%s, item_id=%s)", user_id, item_id)

        response = await self._adelete(f"/users/{user_id}/collected_items/{item_id}")
        response.raise_for_status()
        self._track_response(response)

        logger.info(f"Deleted collected item {item_id} {response.cached_indicator}")
