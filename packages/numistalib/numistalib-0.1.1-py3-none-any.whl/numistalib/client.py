"""Numista API client implementations (sync/async) with caching and throttling.

Provides common logging, dependency injection, cache indicators, rate limiting,
and retry logic for resilient access to the Numista API.

Legal & Attribution
-------------------

- Unofficial: This library is an independent, community project and is not affiliated with Numista.
- Attribution: Numista is a trademark/service of Numista. Please attribute Numista where their data is displayed.
- Compliance: Users must comply with Numista's published terms:
    * Conditions of use: https://en.numista.com/conditions.php
    * Legal information: https://en.numista.com/legal.php
    * Pricing API terms: https://en.numista.com/api/pricing.php
- Pricing API usage considerations: Respect any restrictions on caching, retention, and redistribution of
    pricing responses. Prefer conservative TTLs and avoid republishing price data beyond what Numista permits.
    Configure cache behavior (`default_ttl`, `refresh_ttl_on_access`) accordingly.
"""

import asyncio
import logging
import random
import time
from abc import ABC, abstractmethod
from typing import Any, Protocol

import httpx
from hishel import AsyncSqliteStorage, BaseFilter, FilterPolicy, Request, SyncSqliteStorage
from hishel.httpx import AsyncCacheClient, SyncCacheClient
from pyrate_limiter import Limiter, Rate

# Local constants to avoid circular imports
CACHE_HIT_ICON = "💾"
CACHE_MISS_ICON = "🌐"
DEFAULT_CACHE_DB = "hishel_cache.db"
DEFAULT_CACHE_DIR = ".cache/numistalib/hishel"
DEFAULT_CACHE_REFRESH_ON_ACCESS = True
DEFAULT_CACHE_TTL = 604800  # 7 days
DEFAULT_RATE_LIMIT_PERIOD = 60  # seconds
DEFAULT_RATE_LIMIT_REQUESTS = 45  # requests
DEFAULT_TIMEOUT = 30.0  # seconds
LOGGER_NAME = "numistalib"
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_BACKOFF_BASE = 0.5  # seconds
DEFAULT_BACKOFF_MAX = 5.0   # seconds

logger = logging.getLogger(LOGGER_NAME)


class SyncClientProtocol(Protocol):
    """Synchronous client protocol returning NumistaResponse."""

    def get(self, url: str, **kwargs: Any) -> "NumistaResponse": ...
    def post(self, url: str, **kwargs: Any) -> "NumistaResponse": ...
    def patch(self, url: str, **kwargs: Any) -> "NumistaResponse": ...
    def put(self, url: str, **kwargs: Any) -> "NumistaResponse": ...
    def delete(self, url: str, **kwargs: Any) -> "NumistaResponse": ...


class AsyncClientProtocol(Protocol):
    """Asynchronous client protocol returning NumistaResponse."""

    async def get(self, url: str, **kwargs: Any) -> "NumistaResponse": ...
    async def post(self, url: str, **kwargs: Any) -> "NumistaResponse": ...
    async def patch(self, url: str, **kwargs: Any) -> "NumistaResponse": ...
    async def put(self, url: str, **kwargs: Any) -> "NumistaResponse": ...
    async def delete(self, url: str, **kwargs: Any) -> "NumistaResponse": ...


class CacheAllGETRequests(BaseFilter[Request]):
    """Filter to cache all GET requests regardless of response headers.

    This is designed for legacy APIs (like Numista) that don't send proper
    HTTP caching headers (Cache-Control, ETag, Expires). Per hishel docs,
    FilterPolicy is recommended for legacy APIs that don't implement
    HTTP caching headers correctly.
    """

    def needs_body(self) -> bool:  # noqa: PLR6301
        """Indicate that we don't need to inspect the request body."""
        return False

    def apply(self, item: Request, body: bytes | None) -> bool:  # noqa: ARG002, PLR6301
        """Apply filter: cache all GET requests.

        Parameters
        ----------
        item : Request
            The HTTP request to filter
        body : bytes | None
            Request body (not used)

        Returns
        -------
        bool
            True if request method is GET
        """
        return item.method == "GET"


class NumistaResponse(httpx.Response):
    """Custom HTTP response to expose caching info."""

    @property
    def cached(self) -> bool:
        """Determine if response was served from cache."""
        return bool(self.extensions.get("hishel_from_cache", False))

    @property
    def cached_indicator(self) -> str:
        """Get cache indicator based on response."""
        return str(CACHE_HIT_ICON if self.cached else CACHE_MISS_ICON)


class NumistaClient(ABC):
    """Abstract base for Numista API clients (sync and async).

    Provides caching, rate limiting, and cache indicator tracking.
    """

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        """Initialize Numista client base.

        Parameters
        ----------
        **kwargs : Any
            Configuration parameters
        """
        self.api_key = kwargs.get("api_key")
        self.api_base_url = kwargs.get("api_base_url", "https://api.numista.com/v3")
        self.rate_limit_period = kwargs.get("rate_limit_period", DEFAULT_RATE_LIMIT_PERIOD)
        self.rate_limit_requests = int(kwargs.get("rate_limit_requests", DEFAULT_RATE_LIMIT_REQUESTS))
        self.timeout = int(kwargs.get("timeout", DEFAULT_TIMEOUT))
        self.database_cache_dir = kwargs.get("database_cache_dir", DEFAULT_CACHE_DIR)
        self.database_cache_db = kwargs.get("database_cache_db", DEFAULT_CACHE_DB)
        self.default_ttl = int(kwargs.get("default_ttl", DEFAULT_CACHE_TTL))
        self.refresh_ttl_on_access = kwargs.get("refresh_ttl_on_access", DEFAULT_CACHE_REFRESH_ON_ACCESS)
        self._client: httpx.Client | httpx.AsyncClient | None = None

        if not self.api_key:
            raise ValueError("Numista API key is required via parameter or NUMISTA_API_KEY environment variable")

        self.headers = {
            "Numista-API-Key": self.api_key,
            # "User-Agent": f"numistalib/{__version__}",
        }

        logger.debug(f"{self.__class__.__name__} initialized")

    @property
    def database_full_path(self) -> str:
        """Get the full path to the cache database.

        Creates the cache directory if it doesn't exist.
        """
        from pathlib import Path
        cache_dir = Path(self.database_cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        return str(cache_dir / self.database_cache_db)

    def _build_url(self, path: str) -> str:
        """Build full URL from base and path.

        Parameters
        ----------
        path : str
            API path (relative or absolute URL)

        Returns
        -------
        str
            Full URL
        """
        if path.startswith(("http://", "https://")):
            return path
        return f"{self.api_base_url.rstrip('/')}/{path.lstrip('/')}"

    def _wrap_response(self, response: httpx.Response) -> NumistaResponse:  # noqa: PLR6301
        """Wrap httpx.Response as NumistaResponse to expose cache indicators.

        Parameters
        ----------
        response : httpx.Response
            Raw HTTP response

        Returns
        -------
        NumistaResponse
            Response with cache indicator support
        """
        # Cast the response to NumistaResponse by setting its class
        # This avoids re-reading the response body
        response.__class__ = NumistaResponse
        return response  # type: ignore

    @staticmethod
    def _jitter_delay(attempt: int) -> float:
        """Compute exponential backoff with jitter.

        Parameters
        ----------
        attempt : int
            Zero-based attempt number

        Returns
        -------
        float
            Sleep duration in seconds
        """
        base = DEFAULT_BACKOFF_BASE * (2 ** attempt)
        delay = min(base, DEFAULT_BACKOFF_MAX)
        return float(delay * (0.5 + random.random()))

    @property
    def rate(self) -> Rate:
        """Get the rate limit configuration."""
        return Rate(self.rate_limit_requests, self.rate_limit_period)

    @property
    def limiter(self) -> Limiter:
        """Get the rate limiter instance."""
        return Limiter([self.rate], raise_when_fail=False)

    @property
    @abstractmethod
    def storage(self) -> SyncSqliteStorage | AsyncSqliteStorage:
        """Get the cache storage instance.

        Must be implemented by subclasses.

        Returns
        -------
        SyncSqliteStorage | AsyncSqliteStorage
            Cache storage instance
        """
        pass

    @property
    @abstractmethod
    def client(self) -> httpx.Client | httpx.AsyncClient:
        """Get the HTTP client instance.

        Must be implemented by subclasses.

        Returns
        -------
        httpx.Client | httpx.AsyncClient
            HTTP client instance
        """
        pass


class NumistaClientSync(NumistaClient):
    """Synchronous Numista API client with caching and rate limiting."""

    @property
    def storage(self) -> SyncSqliteStorage:
        """Get the synchronous cache storage instance."""
        return SyncSqliteStorage(
            database_path=self.database_full_path,
            default_ttl=self.default_ttl,
            refresh_ttl_on_access=self.refresh_ttl_on_access,
        )

    @property
    def client(self) -> httpx.Client:
        """Get the synchronous HTTP client instance.

        Caches the client to prevent creating new instances on each request.
        """
        if self._client is None:
            policy = FilterPolicy(request_filters=[CacheAllGETRequests()])
            self._client = SyncCacheClient(
                storage=self.storage,
                headers=self.headers,
                timeout=self.timeout,
                policy=policy,
            )
        return self._client  # type: ignore

    def get(self, url: str, **kwargs: Any) -> NumistaResponse:
        """Make a synchronous GET request.

        Parameters
        ----------
        url : str
            Request URL (relative or absolute)
        **kwargs : Any
            Additional request parameters

        Returns
        -------
        NumistaResponse
            HTTP response with cache indicator
        """
        full_url = self._build_url(url)
        # Retry with exponential backoff and jitter
        for attempt in range(DEFAULT_RETRY_ATTEMPTS):
            try:
                response = self.client.get(full_url, **kwargs)
                return self._wrap_response(response)
            except httpx.HTTPError as err:
                if attempt == DEFAULT_RETRY_ATTEMPTS - 1:
                    raise err
                time.sleep(self._jitter_delay(attempt))
        raise AssertionError("Unreachable: retry loop must return or raise")

    def post(self, url: str, **kwargs: Any) -> NumistaResponse:
        """Make a synchronous POST request.

        Parameters
        ----------
        url : str
            Request URL (relative or absolute)
        **kwargs : Any
            Additional request parameters

        Returns
        -------
        NumistaResponse
            HTTP response with cache indicator
        """
        full_url = self._build_url(url)
        for attempt in range(DEFAULT_RETRY_ATTEMPTS):
            try:
                response = self.client.post(full_url, **kwargs)
                return self._wrap_response(response)
            except httpx.HTTPError as err:
                if attempt == DEFAULT_RETRY_ATTEMPTS - 1:
                    raise err
                time.sleep(self._jitter_delay(attempt))
        raise AssertionError("Unreachable: retry loop must return or raise")

    def patch(self, url: str, **kwargs: Any) -> NumistaResponse:
        """Make a synchronous PATCH request.

        Parameters
        ----------
        url : str
            Request URL (relative or absolute)
        **kwargs : Any
            Additional request parameters

        Returns
        -------
        NumistaResponse
            HTTP response with cache indicator
        """
        full_url = self._build_url(url)
        for attempt in range(DEFAULT_RETRY_ATTEMPTS):
            try:
                response = self.client.patch(full_url, **kwargs)
                return self._wrap_response(response)
            except httpx.HTTPError as err:
                if attempt == DEFAULT_RETRY_ATTEMPTS - 1:
                    raise err
                time.sleep(self._jitter_delay(attempt))
        raise AssertionError("Unreachable: loop must return or raise")

    def put(self, url: str, **kwargs: Any) -> NumistaResponse:
        """Make a synchronous PUT request.

        Parameters
        ----------
        url : str
            Request URL (relative or absolute)
        **kwargs : Any
            Additional request parameters

        Returns
        -------
        NumistaResponse
            HTTP response with cache indicator
        """
        full_url = self._build_url(url)
        for attempt in range(DEFAULT_RETRY_ATTEMPTS):
            try:
                response = self.client.put(full_url, **kwargs)
                return self._wrap_response(response)
            except httpx.HTTPError as err:
                if attempt == DEFAULT_RETRY_ATTEMPTS - 1:
                    raise err
                time.sleep(self._jitter_delay(attempt))
        raise AssertionError("Unreachable: loop must return or raise")

    def delete(self, url: str, **kwargs: Any) -> NumistaResponse:
        """Make a synchronous DELETE request.

        Parameters
        ----------
        url : str
            Request URL (relative or absolute)
        **kwargs : Any
            Additional request parameters

        Returns
        -------
        NumistaResponse
            HTTP response with cache indicator
        """
        full_url = self._build_url(url)
        for attempt in range(DEFAULT_RETRY_ATTEMPTS):
            try:
                response = self.client.delete(full_url, **kwargs)
                return self._wrap_response(response)
            except httpx.HTTPError as err:
                if attempt == DEFAULT_RETRY_ATTEMPTS - 1:
                    raise err
                time.sleep(self._jitter_delay(attempt))
        raise AssertionError("Unreachable: loop must return or raise")


class NumistaClientAsync(NumistaClient):
    """Asynchronous Numista API client with caching and rate limiting."""

    @property
    def storage(self) -> AsyncSqliteStorage:
        """Get the asynchronous cache storage instance."""
        return AsyncSqliteStorage(
            database_path=self.database_full_path,
            default_ttl=self.default_ttl,
            refresh_ttl_on_access=self.refresh_ttl_on_access,
        )

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the asynchronous HTTP client instance.

        Caches the client to prevent creating new instances on each request.
        """
        if self._client is None:
            policy = FilterPolicy(request_filters=[CacheAllGETRequests()])
            self._client = AsyncCacheClient(
                storage=self.storage,
                headers=self.headers,
                timeout=self.timeout,
                policy=policy,
            )
        return self._client  # type: ignore

    async def get(self, url: str, **kwargs: Any) -> NumistaResponse:
        """Make an asynchronous GET request.

        Parameters
        ----------
        url : str
            Request URL (relative or absolute)
        **kwargs : Any
            Additional request parameters

        Returns
        -------
        NumistaResponse
            HTTP response with cache indicator
        """
        full_url = self._build_url(url)
        for attempt in range(DEFAULT_RETRY_ATTEMPTS):
            try:
                response = await self.client.get(full_url, **kwargs)
                return self._wrap_response(response)
            except httpx.HTTPError as err:
                if attempt == DEFAULT_RETRY_ATTEMPTS - 1:
                    raise err
                await asyncio.sleep(self._jitter_delay(attempt))
        raise AssertionError("Unreachable: retry loop must return or raise")

    async def post(self, url: str, **kwargs: Any) -> NumistaResponse:
        """Make an asynchronous POST request.

        Parameters
        ----------
        url : str
            Request URL (relative or absolute)
        **kwargs : Any
            Additional request parameters

        Returns
        -------
        NumistaResponse
            HTTP response with cache indicator
        """
        full_url = self._build_url(url)
        for attempt in range(DEFAULT_RETRY_ATTEMPTS):
            try:
                response = await self.client.post(full_url, **kwargs)
                return self._wrap_response(response)
            except httpx.HTTPError as err:
                if attempt == DEFAULT_RETRY_ATTEMPTS - 1:
                    raise err
                await asyncio.sleep(self._jitter_delay(attempt))
        raise AssertionError("Unreachable: retry loop must return or raise")

    async def patch(self, url: str, **kwargs: Any) -> NumistaResponse:
        """Make an asynchronous PATCH request.

        Parameters
        ----------
        url : str
            Request URL (relative or absolute)
        **kwargs : Any
            Additional request parameters

        Returns
        -------
        NumistaResponse
            HTTP response with cache indicator
        """
        full_url = self._build_url(url)
        for attempt in range(DEFAULT_RETRY_ATTEMPTS):
            try:
                response = await self.client.patch(full_url, **kwargs)
                return self._wrap_response(response)
            except httpx.HTTPError as err:
                if attempt == DEFAULT_RETRY_ATTEMPTS - 1:
                    raise err
                await asyncio.sleep(self._jitter_delay(attempt))
        raise AssertionError("Unreachable: loop must return or raise")

    async def put(self, url: str, **kwargs: Any) -> NumistaResponse:
        """Make an asynchronous PUT request.

        Parameters
        ----------
        url : str
            Request URL (relative or absolute)
        **kwargs : Any
            Additional request parameters

        Returns
        -------
        NumistaResponse
            HTTP response with cache indicator
        """
        full_url = self._build_url(url)
        for attempt in range(DEFAULT_RETRY_ATTEMPTS):
            try:
                response = await self.client.put(full_url, **kwargs)
                return self._wrap_response(response)
            except httpx.HTTPError as err:
                if attempt == DEFAULT_RETRY_ATTEMPTS - 1:
                    raise err
                await asyncio.sleep(self._jitter_delay(attempt))
        raise AssertionError("Unreachable: loop must return or raise")

    async def delete(self, url: str, **kwargs: Any) -> NumistaResponse:
        """Make an asynchronous DELETE request.

        Parameters
        ----------
        url : str
            Request URL (relative or absolute)
        **kwargs : Any
            Additional request parameters

        Returns
        -------
        NumistaResponse
            HTTP response with cache indicator
        """
        full_url = self._build_url(url)
        for attempt in range(DEFAULT_RETRY_ATTEMPTS):
            try:
                response = await self.client.delete(full_url, **kwargs)
                return self._wrap_response(response)
            except httpx.HTTPError as err:
                if attempt == DEFAULT_RETRY_ATTEMPTS - 1:
                    raise err
                await asyncio.sleep(self._jitter_delay(attempt))
        raise AssertionError("Unreachable: loop must return or raise")


class NumistaApiClient:
    """Unified client factory for both sync and async HTTP operations.

    Wraps NumistaClientSync/Async and provides a convenient interface.
    Uses dependency injection pattern for services.
    """

    def __init__(self, client: NumistaClientSync | NumistaClientAsync) -> None:
        """Initialize with a concrete client instance.

        Parameters
        ----------
        client : NumistaClientSync | NumistaClientAsync
            Pre-configured sync or async HTTP client
        """
        self._client = client

    @property
    def is_async(self) -> bool:
        """Check if this is an async client."""
        return isinstance(self._client, NumistaClientAsync)

    @property
    def raw_client(self) -> NumistaClientSync | NumistaClientAsync:
        """Get the underlying raw client."""
        return self._client
