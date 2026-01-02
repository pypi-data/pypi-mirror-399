"""Abstract base classes for Collection service."""

from abc import abstractmethod
from typing import ClassVar

from numistalib.models import CollectedItem, UserCollection
from numistalib.services.base import EntityService


class CollectionServiceBase(EntityService):
    """Abstract interface for collection service operations.

    Enforces both sync and async implementations for all collection queries.
    """

    MODEL_ITEM: ClassVar[type[CollectedItem]] = CollectedItem
    MODEL_COLLECTION: ClassVar[type[UserCollection]] = UserCollection

    @abstractmethod
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
            Filter by category
        type_id : int | None
            Filter by type ID
        collection_id : int | None
            Filter by collection ID

        Returns
        -------
        list[CollectedItem]
            List of collected items
        """
        pass

    @abstractmethod
    def get_collected_item(
        self,
        user_id: int,
        item_id: int,
    ) -> CollectedItem:
        """Get a single collected item.

        Parameters
        ----------
        user_id : int
            Numista user ID
        item_id : int
            Collected item ID

        Returns
        -------
        CollectedItem
            The collected item
        """
        pass

    @abstractmethod
    def get_collections(self, user_id: int) -> list[UserCollection]:
        """Get collections for a user.

        Parameters
        ----------
        user_id : int
            Numista user ID

        Returns
        -------
        list[UserCollection]
            List of user collections
        """
        pass

    @abstractmethod
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
            Filter by category
        type_id : int | None
            Filter by type ID
        collection_id : int | None
            Filter by collection ID

        Returns
        -------
        list[CollectedItem]
            List of collected items
        """
        pass

    @abstractmethod
    async def get_collected_item_async(
        self,
        user_id: int,
        item_id: int,
    ) -> CollectedItem:
        """Get a single collected item (async).

        Parameters
        ----------
        user_id : int
            Numista user ID
        item_id : int
            Collected item ID

        Returns
        -------
        CollectedItem
            The collected item
        """
        pass

    @abstractmethod
    async def get_collections_async(self, user_id: int) -> list[UserCollection]:
        """Get collections for a user (async).

        Parameters
        ----------
        user_id : int
            Numista user ID

        Returns
        -------
        list[UserCollection]
            List of user collections
        """
        pass

    @abstractmethod
    def add_collected_item(self, user_id: int, item_data: dict[str, object]) -> CollectedItem:
        """Add item to user's collection.

        Requires OAuth2 edit_collection scope.
        """
        pass

    @abstractmethod
    async def add_collected_item_async(self, user_id: int, item_data: dict[str, object]) -> CollectedItem:
        """Add item to user's collection (async).

        Requires OAuth2 edit_collection scope.
        """
        pass

    @abstractmethod
    def edit_collected_item(self, user_id: int, item_id: int, item_data: dict[str, object]) -> CollectedItem:
        """Edit item in user's collection.

        Requires OAuth2 edit_collection scope.
        """
        pass

    @abstractmethod
    async def edit_collected_item_async(
        self, user_id: int, item_id: int, item_data: dict[str, object]
    ) -> CollectedItem:
        """Edit item in user's collection (async).

        Requires OAuth2 edit_collection scope.
        """
        pass

    @abstractmethod
    def delete_collected_item(self, user_id: int, item_id: int) -> None:
        """Delete item from user's collection.

        Requires OAuth2 edit_collection scope.
        """
        pass

    @abstractmethod
    async def delete_collected_item_async(self, user_id: int, item_id: int) -> None:
        """Delete item from user's collection (async).

        Requires OAuth2 edit_collection scope.
        """
        pass
