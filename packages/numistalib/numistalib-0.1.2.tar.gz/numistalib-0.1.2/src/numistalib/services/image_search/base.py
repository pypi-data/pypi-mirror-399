"""Abstract base classes for Image Search service."""

from abc import abstractmethod
from typing import ClassVar

from numistalib.models import TypeBasic
from numistalib.services.base import SimpleListService


class ImageSearchServiceBase(SimpleListService):
    """Abstract interface for image search operations.

    Enforces both sync and async implementations.
    """

    MODEL: ClassVar[type[TypeBasic]] = TypeBasic

    @abstractmethod
    def search_by_image(
        self,
        images: list[dict[str, str]],
        category: str | None = None,
        lang: str = "en",
        activate_experimental_features: bool = False,
    ) -> list[TypeBasic]:
        """Search catalogue by image(s).

        Parameters
        ----------
        images : list[dict]
            List of image objects with 'mime_type' and 'image_data' keys
        category : str | None
            Filter by category (coin, banknote, exonumia)
        lang : str
            Language code
        activate_experimental_features : bool
            Enable experimental features (beta)

        Returns
        -------
        list[TypeBasic]
            List of matching types
        """
        pass

    @abstractmethod
    async def search_by_image_async(
        self,
        images: list[dict[str, str]],
        category: str | None = None,
        lang: str = "en",
        activate_experimental_features: bool = False,
    ) -> list[TypeBasic]:
        """Search catalogue by image(s) (async).

        Parameters
        ----------
        images : list[dict]
            List of image objects with 'mime_type' and 'image_data' keys
        category : str | None
            Filter by category (coin, banknote, exonumia)
        lang : str
            Language code
        activate_experimental_features : bool
            Enable experimental features (beta)

        Returns
        -------
        list[TypeBasic]
            List of matching types
        """
        pass
