"""NewsMesh Python SDK - Official client for the NewsMesh News API.

Example usage:
    >>> from newsmesh import NewsMeshClient
    >>> client = NewsMeshClient("your-api-key")
    >>> response = client.get_trending(limit=10)
    >>> for article in response:
    ...     print(article.title)

For async usage:
    >>> from newsmesh import AsyncNewsMeshClient
    >>> async with AsyncNewsMeshClient("your-api-key") as client:
    ...     response = await client.get_trending()
"""

from ._version import __version__
from .client import NewsMeshClient
from .exceptions import (
    AuthenticationError,
    ForbiddenError,
    NewsMeshError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .models import Article, PaginatedResponse

# Lazy import for async client to avoid requiring aiohttp
def __getattr__(name: str):
    if name == "AsyncNewsMeshClient":
        from .async_client import AsyncNewsMeshClient
        return AsyncNewsMeshClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    # Version
    "__version__",
    # Clients
    "NewsMeshClient",
    "AsyncNewsMeshClient",
    # Models
    "Article",
    "PaginatedResponse",
    # Exceptions
    "NewsMeshError",
    "AuthenticationError",
    "ForbiddenError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
]
