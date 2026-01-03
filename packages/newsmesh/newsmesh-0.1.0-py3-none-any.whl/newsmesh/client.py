"""Synchronous client for the NewsMesh API."""

from datetime import date
from typing import Iterator, List, Literal, Optional, Union

from ._http import DEFAULT_BASE_URL, DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT, HTTPClient
from .models import Article, PaginatedResponse


class NewsMeshClient:
    """Synchronous client for the NewsMesh News API.

    Example:
        >>> from newsmesh import NewsMeshClient
        >>> client = NewsMeshClient("your-api-key")
        >>> response = client.get_trending(limit=10)
        >>> for article in response:
        ...     print(article.title)

    The client supports context manager usage for proper cleanup:
        >>> with NewsMeshClient("your-api-key") as client:
        ...     articles = client.get_trending()

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
        """Initialize the NewsMesh client.

        Args:
            api_key: Your NewsMesh API key (required).
            base_url: Base URL for the API.
            timeout: Request timeout in seconds.
            max_retries: Maximum retry attempts for transient failures.
        """
        if not api_key:
            raise ValueError("api_key is required")

        self._http = HTTPClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

    def __enter__(self) -> "NewsMeshClient":
        """Enter context manager."""
        return self

    def __exit__(self, *args) -> None:
        """Exit context manager and close resources."""
        self.close()

    def close(self) -> None:
        """Close the client and release resources."""
        self._http.close()

    def get_trending(
        self,
        *,
        limit: int = 25,
    ) -> PaginatedResponse:
        """Get trending articles.

        Returns the most popular/trending articles from the NewsMesh feed.
        Note: The trending endpoint does not support pagination.

        Args:
            limit: Maximum number of articles to return (1-25, default: 25).

        Returns:
            PaginatedResponse containing trending articles.

        Example:
            >>> response = client.get_trending(limit=10)
            >>> for article in response:
            ...     print(f"{article.title} - {article.source}")
        """
        params = {"limit": min(max(1, limit), 25)}
        data = self._http.get("/trending", params)
        return PaginatedResponse.from_dict(data)

    def get_latest(
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

        Retrieve the newest articles, optionally filtered by category, country,
        or date range.

        Args:
            limit: Maximum number of articles to return (1-25, default: 25).
            category: Filter by category. Can be a single category string or
                list of categories (e.g., "politics" or ["politics", "technology"]).
            country: Filter by ISO 3166-1 alpha-2 country codes (e.g., "us", "gb").
                Can be a single code or list of codes.
            from_date: Start date for filtering (YYYY-MM-DD format or date object).
            to_date: End date for filtering (YYYY-MM-DD format or date object).
            cursor: Pagination cursor from a previous response's next_cursor.

        Returns:
            PaginatedResponse containing articles.

        Example:
            >>> # Get latest tech articles from the US
            >>> response = client.get_latest(
            ...     category="technology",
            ...     country="us",
            ...     limit=10
            ... )
            >>> for article in response:
            ...     print(article.title)
        """
        params = self._build_article_params(
            limit=limit,
            category=category,
            country=country,
            from_date=from_date,
            to_date=to_date,
            cursor=cursor,
        )
        data = self._http.get("/latest", params)
        return PaginatedResponse.from_dict(data)

    def list_articles(
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

        Similar to get_latest() but uses the /article endpoint.

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
        data = self._http.get("/article", params)
        return PaginatedResponse.from_dict(data)

    def get_article(self, article_id: str) -> Article:
        """Get a single article by ID.

        Args:
            article_id: The unique article identifier.

        Returns:
            The Article object.

        Raises:
            NotFoundError: If no article exists with the given ID.

        Example:
            >>> article = client.get_article("abc123")
            >>> print(article.title)
        """
        if not article_id:
            raise ValueError("article_id is required")

        data = self._http.get(f"/article/{article_id}")
        articles = data.get("data", [])
        if not articles:
            from .exceptions import NotFoundError
            raise NotFoundError(
                f"Article not found: {article_id}",
                code="articleNotFound",
                status_code=404,
            )
        return Article.from_dict(articles[0])

    def search(
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

        Perform full-text search across article titles and descriptions.

        Args:
            query: Search query string (required, max 500 characters).
            limit: Maximum number of results (1-25, default: 25).
            from_date: Start date for filtering (YYYY-MM-DD format or date object).
            to_date: End date for filtering (YYYY-MM-DD format or date object).
            sort_by: Sort order - "date_descending" (newest first, default),
                "date_ascending" (oldest first), or "relevant" (most relevant).
            cursor: Pagination cursor from a previous response's next_cursor.

        Returns:
            PaginatedResponse containing matching articles.

        Raises:
            ValidationError: If query is empty or exceeds 500 characters.

        Example:
            >>> # Search for climate-related articles
            >>> response = client.search("climate change", limit=10)
            >>> for article in response:
            ...     print(article.title)
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

        data = self._http.get("/search", params)
        return PaginatedResponse.from_dict(data)

    def paginate(
        self,
        method: str,
        **kwargs,
    ) -> Iterator[Article]:
        """Iterate through all articles across multiple pages.

        Automatically handles pagination by following next_cursor values.

        Args:
            method: The method name to use ("get_latest", "list_articles", or "search").
            **kwargs: Arguments to pass to the underlying method.

        Yields:
            Article objects one at a time.

        Example:
            >>> # Iterate through all tech articles
            >>> for article in client.paginate("get_latest", category="technology"):
            ...     print(article.title)
        """
        method_fn = getattr(self, method, None)
        if method_fn is None or method in ("paginate", "get_article", "get_trending"):
            raise ValueError(f"Invalid method for pagination: {method}")

        cursor = kwargs.pop("cursor", None)

        while True:
            if cursor:
                kwargs["cursor"] = cursor

            response = method_fn(**kwargs)

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
