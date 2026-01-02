"""Abstract base classes for Catalogue service."""

from abc import abstractmethod
from typing import ClassVar

from numistalib.models import Catalogue
from numistalib.services.base import SimpleListService


class CatalogueServiceBase(SimpleListService):
    """Abstract interface for catalogue service operations.

    Enforces both sync and async implementations for all catalogue queries.
    """

    MODEL: ClassVar[type[Catalogue]] = Catalogue

    @abstractmethod
    def get_catalogues(self) -> list[Catalogue]:
        """Get list of all catalogues.

        Returns
        -------
        list[Catalogue]
            List of all catalogues
        """
        pass

    @abstractmethod
    async def get_catalogues_async(self) -> list[Catalogue]:
        """Get list of all catalogues (async).

        Returns
        -------
        list[Catalogue]
            List of all catalogues
        """
        pass
