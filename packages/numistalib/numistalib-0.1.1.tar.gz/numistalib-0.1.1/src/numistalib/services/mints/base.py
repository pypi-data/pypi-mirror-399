"""Abstract base classes for Mint service."""

from abc import abstractmethod
from typing import ClassVar

from numistalib.models import Mint
from numistalib.services.base import SimpleListService


class MintServiceBase(SimpleListService):
    """Abstract interface for mint service operations.

    Enforces both sync and async implementations for all mint queries.
    """

    MODEL: ClassVar[type[Mint]] = Mint

    @abstractmethod
    def get_mints(self, lang: str = "en") -> list[Mint]:
        """Get list of all mints.

        Parameters
        ----------
        lang : str
            Language code (en, es, fr)

        Returns
        -------
        list[Mint]
            List of all mints
        """
        pass

    @abstractmethod
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
        """
        pass

    @abstractmethod
    def get_mint(self, mint_id: int) -> Mint:
        """Get details about a specific mint.

        Parameters
        ----------
        mint_id : int
            Numista mint ID

        Returns
        -------
        Mint
            Mint details
        """
        pass

    @abstractmethod
    async def get_mint_async(self, mint_id: int) -> Mint:
        """Get details about a specific mint (async).

        Parameters
        ----------
        mint_id : int
            Numista mint ID

        Returns
        -------
        Mint
            Mint details
        """
        pass
