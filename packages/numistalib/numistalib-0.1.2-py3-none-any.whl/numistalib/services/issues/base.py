"""Abstract base classes for Issue service."""

from abc import abstractmethod
from collections.abc import Mapping
from typing import Any, ClassVar

from numistalib.models import Issue
from numistalib.services.base import NestedResourceService


class IssueServiceBase(NestedResourceService):
    """Abstract interface for issue service operations.

    Enforces both sync and async implementations for all issue queries.
    Pagination is supported via paginated_issues async generator method.
    """

    MODEL: ClassVar[type[Issue]] = Issue

    @abstractmethod
    def get_issues(self, type_id: int, lang: str = "en") -> list[Issue]:
        """Get all issues for a specific type (single call)."""
        pass

    @abstractmethod
    def add_issue(
        self,
        type_id: int,
        issue_data: Mapping[str, Any],
        lang: str | None = None,
    ) -> Issue:
        """Add a new issue to a type."""
        pass

    @abstractmethod
    async def get_issues_async(self, type_id: int, lang: str = "en") -> list[Issue]:
        """Get all issues for a specific type (async)."""
        pass

    @abstractmethod
    async def add_issue_async(
        self,
        type_id: int,
        issue_data: Mapping[str, Any],
        lang: str | None = None,
    ) -> Issue:
        """Add a new issue to a type (async)."""
        pass
