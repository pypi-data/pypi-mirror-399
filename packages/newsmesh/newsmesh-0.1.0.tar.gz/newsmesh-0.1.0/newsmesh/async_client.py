"""Asynchronous client for the NewsMesh API."""

import random
from datetime import date
from typing import Any, AsyncIterator, Dict, List, Literal, Optional, Union

from ._http import DEFAULT_BASE_URL, DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT
from .exceptions import (
    NewsMeshError,
    RateLimitError,
    ServerError,
    raise_for_error,
)
from .models import Article, PaginatedResponse

# aiohttp is optional
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False


DEFAULT_RETRY_STATUSES = {429, 500, 502, 503, 504}


class AsyncNewsMeshClient:
    """Asynchronous client for the NewsMesh News API.

    Requires the 'async' extra: pip install newsmesh[async]

    Example:
        >>> import asyncio
        >>> from newsmesh import AsyncNewsMeshClient
        >>>
        >>> async def main():
        ...     async with AsyncNewsMeshClient("your-api-key") as client:
        ...         response = await client.get_trending(limit=10)
        ...         for article in response:
        ...             print(article.title)
        >>>
        >>> asyncio.run(main())

    Attributes:
        api_key: Your NewsMesh API key.
        base_url: Base URL for the API (default: https://api.newsmesh.co/v1).
        timeout: Request timeout in seconds (default: 30).
        max_retries: Maximum retry attempts for transient failures (default: 3).
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        """Initialize the async NewsMesh client.

        Args:
            api_key: Your NewsMesh API key (required).
            base_url: Base URL for the API.
            timeout: Request timeout in seconds.
            max_retries: Maximum retry attempts for transient failures.

        Raises:
            ImportError: If aiohttp is not installed.
        """
        if not HAS_AIOHTTP:
            raise ImportError(
                "aiohttp is required for async support. "
                "Install it with: pip install newsmesh[async]"
            )

        if not api_key:
            raise ValueError("api_key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "AsyncNewsMeshClient":
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args) -> None:
        """Exit async context manager and close resources."""
        await self.close()

    async def close(self) -> None:
        """Close the client and release resources."""
        if self._session is not None and not self._session.closed:
            await self._session.close()
            self._session = None

    async def _get_session(self) -> "aiohttp.ClientSession":
        """Get or create the aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    "User-Agent": "newsmesh-python/0.1.0",
                    "Accept": "application/json",
                },
            )
        return self._session

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request with automatic retries.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: API endpoint path (e.g., "/trending").
            params: Query parameters to include.

        Returns:
            The JSON response as a dictionary.

        Raises:
            NewsMeshError: On API errors or after max retries exhausted.
        """
        import asyncio

        url = f"{self.base_url}{path}"

        if params is None:
            params = {}
        params["apiKey"] = self.api_key

        session = await self._get_session()
        last_exception: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                async with session.request(method, url, params=params) as response:
                    try:
                        data = await response.json()
                    except Exception:
                        data = {}

                    if response.status >= 400:
                        if (
                            response.status in DEFAULT_RETRY_STATUSES
                            and attempt < self.max_retries
                        ):
                            await self._wait_for_retry(attempt, response)
                            continue

                        if data.get("status") == "error":
                            raise_for_error(data, response.status)
                        else:
                            if response.status == 429:
                                raise RateLimitError(
                                    "Rate limit exceeded",
                                    status_code=response.status,
                                )
                            elif response.status >= 500:
                                raise ServerError(
                                    f"Server error: {response.status}",
                                    status_code=response.status,
                                )
                            else:
                                raise NewsMeshError(
                                    f"HTTP error: {response.status}",
                                    status_code=response.status,
                                )

                    return data

            except asyncio.TimeoutError as e:
                last_exception = e
                if attempt < self.max_retries:
                    await self._wait_for_retry(attempt)
                    continue
                raise NewsMeshError(f"Request timed out") from e

            except aiohttp.ClientError as e:
                last_exception = e
                if attempt < self.max_retries:
                    await self._wait_for_retry(attempt)
                    continue
                raise NewsMeshError(f"Connection error: {e}") from e

            except NewsMeshError:
                raise

            except Exception as e:
                last_exception = e
                raise NewsMeshError(f"Unexpected error: {e}") from e

        raise NewsMeshError(
            f"Max retries ({self.max_retries}) exceeded"
        ) from last_exception

    async def _wait_for_retry(
        self,
        attempt: int,
        response: Optional["aiohttp.ClientResponse"] = None,
    ) -> None:
        """Wait before retrying with exponential backoff and jitter."""
        import asyncio

        if response is not None:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    wait_time = float(retry_after)
                    await asyncio.sleep(wait_time)
                    return
                except ValueError:
                    pass

        base_wait = 0.5 * (2 ** attempt)
        jitter = random.uniform(0, 0.5 * base_wait)
        await asyncio.sleep(base_wait + jitter)

    async def get_trending(
        self,
        *,
        limit: int = 25,
    ) -> PaginatedResponse:
        """Get trending articles.

        Returns the most popular/trending articles from the NewsMesh feed.

        Args:
            limit: Maximum number of articles to return (1-25, default: 25).

        Returns:
            PaginatedResponse containing trending articles.
        """
        params = {"limit": min(max(1, limit), 25)}
        data = await self._request("GET", "/trending", params)
        return PaginatedResponse.from_dict(data)

    async def get_latest(
        self,
        *,
        limit: int = 25,
        category: Optional[Union[str, List[str]]] = None,
        country: Optional[Union[str, List[str]]] = None,
        from_date: Optional[Union[str, date]] = None,
        to_date: Optional[Union[str, date]] = None,
        cursor: Optional[str] = None,
    ) -> PaginatedResponse:
        """Get the latest articles.

        Args:
            limit: Maximum number of articles to return (1-25, default: 25).
            category: Filter by category or list of categories.
            country: Filter by ISO 3166-1 alpha-2 country codes.
            from_date: Start date for filtering (YYYY-MM-DD format or date object).
            to_date: End date for filtering (YYYY-MM-DD format or date object).
            cursor: Pagination cursor from a previous response's next_cursor.

        Returns:
            PaginatedResponse containing articles.
        """
        params = self._build_article_params(
            limit=limit,
            category=category,
            country=country,
            from_date=from_date,
            to_date=to_date,
            cursor=cursor,
        )
        data = await self._request("GET", "/latest", params)
        return PaginatedResponse.from_dict(data)

    async def list_articles(
        self,
        *,
        limit: int = 25,
        category: Optional[Union[str, List[str]]] = None,
        country: Optional[Union[str, List[str]]] = None,
        from_date: Optional[Union[str, date]] = None,
        to_date: Optional[Union[str, date]] = None,
        cursor: Optional[str] = None,
    ) -> PaginatedResponse:
        """List articles with filters.

        Args:
            limit: Maximum number of articles to return (1-25, default: 25).
            category: Filter by category or list of categories.
            country: Filter by ISO 3166-1 alpha-2 country codes.
            from_date: Start date for filtering (YYYY-MM-DD format or date object).
            to_date: End date for filtering (YYYY-MM-DD format or date object).
            cursor: Pagination cursor from a previous response's next_cursor.

        Returns:
            PaginatedResponse containing articles.
        """
        params = self._build_article_params(
            limit=limit,
            category=category,
            country=country,
            from_date=from_date,
            to_date=to_date,
            cursor=cursor,
        )
        data = await self._request("GET", "/article", params)
        return PaginatedResponse.from_dict(data)

    async def get_article(self, article_id: str) -> Article:
        """Get a single article by ID.

        Args:
            article_id: The unique article identifier.

        Returns:
            The Article object.

        Raises:
            NotFoundError: If no article exists with the given ID.
        """
        if not article_id:
            raise ValueError("article_id is required")

        data = await self._request("GET", f"/article/{article_id}")
        articles = data.get("data", [])
        if not articles:
            from .exceptions import NotFoundError
            raise NotFoundError(
                f"Article not found: {article_id}",
                code="articleNotFound",
                status_code=404,
            )
        return Article.from_dict(articles[0])

    async def search(
        self,
        query: str,
        *,
        limit: int = 25,
        from_date: Optional[Union[str, date]] = None,
        to_date: Optional[Union[str, date]] = None,
        sort_by: Literal["date_descending", "date_ascending", "relevant"] = "date_descending",
        cursor: Optional[str] = None,
    ) -> PaginatedResponse:
        """Search articles by keyword.

        Args:
            query: Search query string (required, max 500 characters).
            limit: Maximum number of results (1-25, default: 25).
            from_date: Start date for filtering (YYYY-MM-DD format or date object).
            to_date: End date for filtering (YYYY-MM-DD format or date object).
            sort_by: Sort order - "date_descending", "date_ascending", or "relevant".
            cursor: Pagination cursor from a previous response's next_cursor.

        Returns:
            PaginatedResponse containing matching articles.

        Raises:
            ValidationError: If query is empty or exceeds 500 characters.
        """
        if not query or not query.strip():
            from .exceptions import ValidationError
            raise ValidationError(
                "Search query is required",
                code="queryMissing",
                status_code=400,
            )

        if len(query) > 500:
            from .exceptions import ValidationError
            raise ValidationError(
                "Search query must be 500 characters or less",
                code="queryTooLong",
                status_code=400,
            )

        params = {
            "q": query.strip(),
            "limit": min(max(1, limit), 25),
            "sortBy": sort_by,
        }

        if from_date:
            params["from"] = self._format_date(from_date)
        if to_date:
            params["to"] = self._format_date(to_date)
        if cursor:
            params["cursor"] = cursor

        data = await self._request("GET", "/search", params)
        return PaginatedResponse.from_dict(data)

    async def paginate(
        self,
        method: str,
        **kwargs,
    ) -> AsyncIterator[Article]:
        """Iterate through all articles across multiple pages.

        Args:
            method: The method name ("get_latest", "list_articles", or "search").
            **kwargs: Arguments to pass to the underlying method.

        Yields:
            Article objects one at a time.

        Example:
            >>> async for article in client.paginate("get_latest", category="tech"):
            ...     print(article.title)
        """
        method_fn = getattr(self, method, None)
        if method_fn is None or method in ("paginate", "get_article", "get_trending"):
            raise ValueError(f"Invalid method for pagination: {method}")

        cursor = kwargs.pop("cursor", None)

        while True:
            if cursor:
                kwargs["cursor"] = cursor

            response = await method_fn(**kwargs)

            for article in response.data:
                yield article

            if not response.has_more:
                break

            cursor = response.next_cursor

    def _build_article_params(
        self,
        limit: int,
        category: Optional[Union[str, List[str]]],
        country: Optional[Union[str, List[str]]],
        from_date: Optional[Union[str, date]],
        to_date: Optional[Union[str, date]],
        cursor: Optional[str],
    ) -> dict:
        """Build query parameters for article listing endpoints."""
        params = {"limit": min(max(1, limit), 25)}

        if category:
            if isinstance(category, list):
                params["category"] = ",".join(category)
            else:
                params["category"] = category

        if country:
            if isinstance(country, list):
                params["country"] = ",".join(country)
            else:
                params["country"] = country

        if from_date:
            params["from"] = self._format_date(from_date)

        if to_date:
            params["to"] = self._format_date(to_date)

        if cursor:
            params["cursor"] = cursor

        return params

    @staticmethod
    def _format_date(d: Union[str, date]) -> str:
        """Format a date as YYYY-MM-DD string."""
        if isinstance(d, date):
            return d.strftime("%Y-%m-%d")
        return d
