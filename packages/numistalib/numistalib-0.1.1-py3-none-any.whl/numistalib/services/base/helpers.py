"""Client type protocols for dependency injection."""

from typing import Any, Protocol

from numistalib.client import NumistaResponse


class SyncClientProtocol(Protocol):
    """Protocol for synchronous HTTP client."""

    def get(
        self, url: str, params: dict[str, Any] | None = None
    ) -> NumistaResponse:
        """Send GET request.

        Parameters
        ----------
        url : str
            Endpoint URL
        params : dict[str, Any] | None
            Query parameters

        Returns
        -------
        NumistaResponse
            HTTP response with caching metadata
        """
        ...

    def post(
        self, url: str, params: dict[str, Any] | None = None, json: Any = None
    ) -> NumistaResponse:
        """Send POST request.

        Parameters
        ----------
        url : str
            Endpoint URL
        params : dict[str, Any] | None
            Query parameters
        json : Any
            JSON body

        Returns
        -------
        NumistaResponse
            HTTP response with caching metadata
        """
        ...


class AsyncClientProtocol(Protocol):
    """Protocol for asynchronous HTTP client."""

    async def get(
        self, url: str, params: dict[str, Any] | None = None
    ) -> NumistaResponse:
        """Send async GET request.

        Parameters
        ----------
        url : str
            Endpoint URL
        params : dict[str, Any] | None
            Query parameters

        Returns
        -------
        NumistaResponse
            HTTP response with caching metadata
        """
        ...

    async def post(
        self, url: str, params: dict[str, Any] | None = None, json: Any = None
    ) -> NumistaResponse:
        """Send async POST request.

        Parameters
        ----------
        url : str
            Endpoint URL
        params : dict[str, Any] | None
            Query parameters
        json : Any
            JSON body

        Returns
        -------
        NumistaResponse
            HTTP response with caching metadata
        """
        ...
