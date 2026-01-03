"""Data models for the NewsMesh API."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Article:
    """Represents a news article from NewsMesh.

    Attributes:
        article_id: Unique identifier for the article.
        title: The headline of the article.
        description: A brief summary or blurb of the article.
        link: URL to the original article.
        published_date: When the article was published (ISO 8601 format).
        source: The news source/publisher name.
        category: The article's category (e.g., "politics", "technology").
        topics: List of topics/tags associated with the article.
        media_url: URL to the article's featured image, if available.
        people: List of people mentioned in the article, if available.
        author: The article's author, if available.
    """

    article_id: str
    title: str
    description: str
    link: str
    published_date: str
    source: str
    category: str
    topics: List[str]
    media_url: Optional[str] = None
    people: Optional[List[str]] = None
    author: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Article":
        """Create an Article from an API response dictionary."""
        return cls(
            article_id=data["article_id"],
            title=data["title"],
            description=data["description"],
            link=data["link"],
            published_date=data["published_date"],
            source=data["source"],
            category=data["category"],
            topics=data.get("topics", []),
            media_url=data.get("media_url"),
            people=data.get("people"),
            author=data.get("author"),
        )

    @property
    def published_datetime(self) -> datetime:
        """Parse published_date as a datetime object."""
        # Handle ISO 8601 format with or without microseconds
        for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"]:
            try:
                return datetime.strptime(self.published_date, fmt)
            except ValueError:
                continue
        # Fallback: try fromisoformat (Python 3.7+)
        return datetime.fromisoformat(self.published_date.replace("Z", "+00:00"))


@dataclass
class PaginatedResponse:
    """Response containing a list of articles with pagination support.

    Attributes:
        data: List of Article objects.
        next_cursor: Cursor for fetching the next page, or None if no more results.
    """

    data: List[Article]
    next_cursor: Optional[str] = None

    @classmethod
    def from_dict(cls, response: dict) -> "PaginatedResponse":
        """Create a PaginatedResponse from an API response dictionary."""
        articles = [Article.from_dict(item) for item in response.get("data", [])]
        return cls(data=articles, next_cursor=response.get("next_cursor"))

    def __iter__(self):
        """Iterate over the articles in this response."""
        return iter(self.data)

    def __len__(self) -> int:
        """Return the number of articles in this response."""
        return len(self.data)

    def __bool__(self) -> bool:
        """Return True if there are articles in this response."""
        return len(self.data) > 0

    @property
    def has_more(self) -> bool:
        """Return True if there are more pages available."""
        return self.next_cursor is not None
