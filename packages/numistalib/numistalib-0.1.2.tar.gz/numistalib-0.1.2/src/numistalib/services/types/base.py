"""Abstract base classes for Type service."""

from abc import abstractmethod
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, ClassVar

from numistalib.models.types import TypeBasic, TypeFull
from numistalib.services.base import BaseService

if TYPE_CHECKING:
    from numistalib.services.types.service import SearchParams


class TypeBasicServiceBase(BaseService):
    """Abstract interface for type catalogue search operations."""

    MODEL_BASIC: ClassVar[type[TypeBasic]] = TypeBasic

    @abstractmethod
    def search_types(self, params: "SearchParams") -> list[TypeBasic]:
        """Search catalogue types by various criteria (single page)."""
        pass

    @abstractmethod
    async def search_types_async(self, params: "SearchParams") -> list[TypeBasic]:
        """Search catalogue types by various criteria (async)."""
        pass

    @abstractmethod
    async def paginated_search(self, params: "SearchParams") -> AsyncGenerator[TypeBasic]:
        """Lazily search catalogue types across pages (async)."""
        ...
        yield  # type: ignore[misc]

    @abstractmethod
    async def search_types_paginated(
        self,
        query: str | None = None,
        issuer: str | None = None,
        year: int | None = None,
        category: str | None = None,
        limit: int = 50,
    ) -> AsyncGenerator[TypeBasic]:
        """Convenience wrapper for paginated type search (async)."""
        ...
        yield  # type: ignore[misc]


class TypeFullServiceBase(BaseService):
    """Abstract interface for type detail and mutation operations."""

    MODEL_FULL: ClassVar[type[TypeFull]] = TypeFull

    @abstractmethod
    def get_type(self, type_id: int) -> TypeFull:
        """Get full details about a specific type."""
        pass

    @abstractmethod
    async def get_type_async(self, type_id: int) -> TypeFull:
        """Get full details about a specific type (async)."""
        pass

    @abstractmethod
    def add_type(self, type_data: dict[str, object], lang: str | None = None) -> TypeFull:
        """Add a new type to the catalogue."""
        pass

    @abstractmethod
    async def add_type_async(self, type_data: dict[str, object], lang: str | None = None) -> TypeFull:
        """Add a new type to the catalogue (async)."""
        pass


class TypeServiceBase(TypeBasicServiceBase, TypeFullServiceBase):
    """Composite interface for full type service (search + detail)."""

    MODEL_BASIC: ClassVar[type[TypeBasic]] = TypeBasic
    MODEL_FULL: ClassVar[type[TypeFull]] = TypeFull
