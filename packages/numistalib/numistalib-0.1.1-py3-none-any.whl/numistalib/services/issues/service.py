"""Issue service implementation."""

from collections.abc import AsyncGenerator, Mapping
from typing import Any, cast

from numistalib import logger
from numistalib.client import AsyncClientProtocol, NumistaResponse, SyncClientProtocol
from numistalib.models.issues import Issue, Mark, Signature
from numistalib.models.references import Catalogue, Reference
from numistalib.services.issues.base import IssueServiceBase


class IssueService(IssueServiceBase):
    """Unified issue service supporting both sync and async clients."""

    CLASS_ITEMS_KEY = "issues"

    def __init__(self, client: SyncClientProtocol | AsyncClientProtocol) -> None:
        """Initialize issue service.

        Parameters
        ----------
        client : SyncClientProtocol | AsyncClientProtocol
            HTTP client instance (sync or async)
        """
        super().__init__(client)

    def to_models(  # noqa: PLR6301
        self, items: list[Mapping[str, Any]], type_id: int | None = None, **kwargs: Any  # noqa: ARG002
    ) -> list[Issue]:
        """Convert API response items to Issue models.

        Parameters
        ----------
        items : list[Mapping[str, Any]]
            Raw API response items
        type_id : int | None
            Numista type ID (required context)
        **kwargs : Any
            Additional context

        Returns
        -------
        list[Issue]
            Parsed issue models
        """
        if type_id is None:
            raise ValueError("type_id is required for issue conversion")

        issues: list[Issue] = []
        for item in items:
            # Parse marks array
            marks_data = item.get("marks", [])
            marks = [
                Mark(
                    mark_id=mark["id"],
                    title=mark.get("title"),
                    picture=mark.get("picture"),
                    letters=mark.get("letters"),
                )
                for mark in marks_data
            ]

            # Parse signatures array
            signatures_data = item.get("signatures", [])
            signatures = [
                Signature(
                    signer_name=sig["signer_name"],
                    signer_title=sig.get("signer_title"),
                )
                for sig in signatures_data
            ]

            # Parse references array
            references_data = item.get("references", [])
            references = [
                Reference(
                    catalogue=Catalogue(
                        id=ref["catalogue"]["id"],
                        code=ref["catalogue"]["code"],
                    ),
                    number=ref["number"],
                    url=ref.get("url"),
                )
                for ref in references_data
            ]

            issues.append(
                Issue(
                    numista_id=cast(int, item["id"]),
                    type_id=type_id,
                    is_dated=cast(bool | None, item.get("is_dated")) or False,
                    year=cast(int | None, item.get("year")),
                    gregorian_year=cast(int | None, item.get("gregorian_year")),
                    min_year=cast(int | None, item.get("min_year")),
                    max_year=cast(int | None, item.get("max_year")),
                    mint_letter=cast(str | None, item.get("mint_letter")),
                    marks=marks,
                    signatures=signatures,
                    mintage=cast(int | None, item.get("mintage")),
                    references=references,
                    comment=cast(str | None, item.get("comment")),
                )
            )
        return issues

    def get_issues(self, type_id: int, lang: str = "en") -> list[Issue]:
        """Get all issues for a specific type (single call).

        Supports both sync and async clients via duck-typing.

        Parameters
        ----------
        type_id : int
            Numista type ID
        lang : str
            Language code

        Returns
        -------
        list[Issue]
            List of issues

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ get_issues(type_id=%s, lang=%s)", type_id, lang)

        params = self._build_params(lang=lang) if lang else None
        response = cast(
            NumistaResponse,
            self._client.get(f"/types/{type_id}/issues", params=params),
        )
        response.raise_for_status()
        self._track_response(response)
        data = response.json()

        items = cast(list[Mapping[str, Any]], data) if isinstance(data, list) else cast(
            list[Mapping[str, Any]], data.get("issues", [])
        )
        issues = self.to_models(items, type_id=type_id)

        logger.info(
            f"Retrieved {len(issues)} issues for type {type_id} {response.cached_indicator}"
        )
        return issues

    def add_issue(
        self,
        type_id: int,
        issue_data: Mapping[str, Any],
        lang: str | None = None,
    ) -> Issue:
        """Add a new issue to a type.

        Parameters
        ----------
        type_id : int
            Numista type ID
        issue_data : Mapping[str, Any]
            Issue data payload
        lang : str | None
            Language code

        Returns
        -------
        Issue
            Created issue

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ add_issue(type_id=%s, lang=%s)", type_id, lang)

        params = self._build_params(lang=lang) if lang else None
        response = cast(
            NumistaResponse,
            self._client.post(
                f"/types/{type_id}/issues", params=params, json=dict(issue_data)
            ),
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        issue = self.to_models([data], type_id=type_id)[0]

        logger.info(
            f"Added issue {issue.numista_id} for type {type_id} {response.cached_indicator}"
        )
        return issue

    async def get_issues_async(self, type_id: int, lang: str = "en") -> list[Issue]:
        """Get all issues for a specific type (async).

        Parameters
        ----------
        type_id : int
            Numista type ID
        lang : str
            Language code

        Returns
        -------
        list[Issue]
            List of issues

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ get_issues_async(type_id=%s, lang=%s)", type_id, lang)

        params = self._build_params(lang=lang) if lang else None
        response = await self._aget(f"/types/{type_id}/issues", params=params)
        response.raise_for_status()
        self._track_response(response)
        data = response.json()

        items = cast(list[Mapping[str, Any]], data) if isinstance(data, list) else cast(
            list[Mapping[str, Any]], data.get("issues", [])
        )
        issues = self.to_models(items, type_id=type_id)

        logger.info(
            f"Retrieved {len(issues)} issues for type {type_id} {response.cached_indicator}"
        )
        return issues

    async def add_issue_async(
        self,
        type_id: int,
        issue_data: Mapping[str, Any],
        lang: str | None = None,
    ) -> Issue:
        """Add a new issue to a type (async).

        Parameters
        ----------
        type_id : int
            Numista type ID
        issue_data : Mapping[str, Any]
            Issue data payload
        lang : str | None
            Language code

        Returns
        -------
        Issue
            Created issue

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ add_issue_async(type_id=%s, lang=%s)", type_id, lang)

        params = self._build_params(lang=lang) if lang else None
        response = await self._apost(
            f"/types/{type_id}/issues", params=params, json=dict(issue_data)
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        issue = self.to_models([data], type_id=type_id)[0]

        logger.info(
            f"Added issue {issue.numista_id} for type {type_id} {response.cached_indicator}"
        )
        return issue

    async def paginated_issues(
        self,
        type_id: int,
        lang: str = "en",
        limit: int = 100,
    ) -> AsyncGenerator[Issue]:
        """Lazily iterate issues by following pagination links.

        Parameters
        ----------
        type_id : int
            Numista type ID
        lang : str
            Language code
        limit : int
            Results per page (max 100)

        Yields
        ------
        Issue
            Individual issue records
        """
        logger.debug(
            "→ paginated_issues(type_id=%s, lang=%s, limit=%s)", type_id, lang, limit
        )

        url: str | None = f"/types/{type_id}/issues?lang={lang}&count={limit}"
        page_count = 0

        while url:
            page_count += 1
            logger.debug("Fetching issues page %s: %s", page_count, url)

            response = await self._aget(url)
            response.raise_for_status()
            self._track_response(response)

            data = response.json()
            if isinstance(data, list):
                items = cast(list[Mapping[str, Any]], data)
                next_url = None
            else:
                mapping = cast(Mapping[str, Any], data)
                items = cast(list[Mapping[str, Any]], mapping.get(self.CLASS_ITEMS_KEY, []))
                next_url = cast(str | None, mapping.get("next_url"))

            issues = self.to_models(items, type_id=type_id)
            for issue in issues:
                yield issue

            url = next_url

        logger.info("Finished paginating through %s pages of issues", page_count)

    async def get_issues_paginated(
        self,
        type_id: int,
        lang: str = "en",
        limit: int = 100,
    ) -> AsyncGenerator[Issue]:
        """Paginate through issues for a type (alias for paginated_issues).

        Parameters
        ----------
        type_id : int
            Numista type ID
        lang : str
            Language code
        limit : int
            Results per page (max 100)

        Yields
        ------
        Issue
            Individual issue records
        """
        async for issue in self.paginated_issues(type_id=type_id, lang=lang, limit=limit):
            yield issue


# Backward compatibility exports
IssueServiceAsync = IssueService
