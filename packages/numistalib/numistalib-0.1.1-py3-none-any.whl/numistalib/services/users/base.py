"""Abstract base classes for User service."""

from abc import abstractmethod
from typing import Any, ClassVar

from numistalib.models import CollectedItem, User
from numistalib.services.base import EntityService


class UserServiceBase(EntityService):
    """Abstract interface for user service operations.

    Enforces both sync and async implementations for all user queries.
    """

    MODEL_USER: ClassVar[type[User]] = User
    MODEL_COLLECTED_ITEM: ClassVar[type[CollectedItem]] = CollectedItem

    @abstractmethod
    def get_user(self, user_id: int) -> User:
        """Get details about a specific user.

        Parameters
        ----------
        user_id : int
            Numista user ID

        Returns
        -------
        User
            User profile details
        """
        pass

    @abstractmethod
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
        """
        pass

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
            Filter by category (coin, banknote, exonumia)
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
        """
        pass

    @abstractmethod
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
            Filter by category (coin, banknote, exonumia)
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
