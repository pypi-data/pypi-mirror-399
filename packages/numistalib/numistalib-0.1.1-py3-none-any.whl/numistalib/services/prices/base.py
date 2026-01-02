"""Abstract base classes for Price service."""

from abc import abstractmethod
from typing import ClassVar

from numistalib.models import Price
from numistalib.services.base import NestedResourceService


class PriceServiceBase(NestedResourceService):
    """Abstract interface for price service operations.

    Enforces both sync and async implementations for all price queries.
    """

    MODEL: ClassVar[type[Price]] = Price

    @abstractmethod
    def get_prices(
        self,
        type_id: int,
        issue_id: int,
        *,
        currency: str | None = None,
        lang: str | None = None,
    ) -> list[Price]:
        """Get price estimates for a specific issue.

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
        """
        pass

    @abstractmethod
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
        """
        pass
