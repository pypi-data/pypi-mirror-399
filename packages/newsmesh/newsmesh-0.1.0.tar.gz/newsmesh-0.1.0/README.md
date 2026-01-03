# NewsMesh Python SDK

Official Python SDK for the [NewsMesh News API](https://newsmesh.co).

## Installation

```bash
pip install newsmesh
```

For async support:
```bash
pip install newsmesh[async]
```

## Quick Start

```python
from newsmesh import NewsMeshClient

client = NewsMeshClient("your-api-key")

# Get trending articles
trending = client.get_trending(limit=10)
for article in trending:
    print(f"{article.title} - {article.source}")
```

## Features

- **Sync and Async clients** - Choose based on your application needs
- **Type hints** - Full type annotations for IDE support
- **Automatic retries** - Exponential backoff on transient failures
- **Pagination helpers** - Easy iteration through large result sets
- **Custom exceptions** - Granular error handling

## Usage

### Initialize the Client

```python
from newsmesh import NewsMeshClient

# Basic initialization
client = NewsMeshClient("your-api-key")

# With custom settings
client = NewsMeshClient(
    "your-api-key",
    timeout=60.0,      # Request timeout in seconds
    max_retries=5,     # Max retry attempts
)

# Using context manager (recommended)
with NewsMeshClient("your-api-key") as client:
    articles = client.get_trending()
```

### Get Trending Articles

```python
response = client.get_trending(limit=10)

for article in response:
    print(article.title)
    print(article.description)
    print(article.link)
    print("---")
```

### Get Latest Articles

```python
# Basic usage
response = client.get_latest(limit=25)

# With filters
response = client.get_latest(
    category="technology",           # Single category
    country="us",                    # ISO 3166-1 alpha-2 code
    limit=10,
)

# Multiple categories and countries
response = client.get_latest(
    category=["politics", "world"],
    country=["us", "gb"],
)

# With date range
from datetime import date

response = client.get_latest(
    from_date="2025-01-01",          # String format
    to_date=date(2025, 1, 31),       # Or date object
)
```

### Search Articles

```python
# Basic search
response = client.search("climate change")

# With options
response = client.search(
    "artificial intelligence",
    limit=20,
    sort_by="relevant",              # "date_descending", "date_ascending", "relevant"
    from_date="2025-01-01",
)
```

### Get Single Article

```python
article = client.get_article("article-id-123")
print(article.title)
```

### Pagination

```python
# Manual pagination
response = client.get_latest(limit=25)
while response.has_more:
    for article in response:
        print(article.title)
    response = client.get_latest(cursor=response.next_cursor)

# Automatic pagination with iterator
for article in client.paginate("get_latest", category="technology"):
    print(article.title)
```

## Async Usage

```python
import asyncio
from newsmesh import AsyncNewsMeshClient

async def main():
    async with AsyncNewsMeshClient("your-api-key") as client:
        # Get trending
        trending = await client.get_trending()

        # Search
        results = await client.search("tech news")

        # Paginate
        async for article in client.paginate("get_latest"):
            print(article.title)

asyncio.run(main())
```

## Error Handling

```python
from newsmesh import (
    NewsMeshClient,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
)

client = NewsMeshClient("your-api-key")

try:
    article = client.get_article("invalid-id")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}")
except NotFoundError:
    print("Article not found")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
```

## Article Properties

```python
article = client.get_article("some-id")

article.article_id       # Unique identifier
article.title            # Headline
article.description      # Summary/blurb
article.link             # URL to original article
article.published_date   # ISO 8601 timestamp string
article.published_datetime  # As datetime object
article.source           # Publisher name
article.category         # Category (e.g., "technology")
article.topics           # List of topics/tags
article.media_url        # Featured image URL (may be None)
article.people           # People mentioned (may be None)
article.author           # Author name (may be None)
```

## API Reference

| Method | Description |
|--------|-------------|
| `get_trending(limit)` | Get trending articles |
| `get_latest(limit, category, country, from_date, to_date, cursor)` | Get latest articles with filters |
| `list_articles(...)` | List articles (alias for get_latest) |
| `get_article(article_id)` | Get single article by ID |
| `search(query, limit, from_date, to_date, sort_by, cursor)` | Full-text search |
| `paginate(method, **kwargs)` | Auto-paginate through results |

## Supported Countries

Filter by ISO 3166-1 alpha-2 codes:

`ae`, `au`, `be`, `br`, `ca`, `cn`, `co`, `de`, `eg`, `fr`, `gb`, `hk`, `id`, `ie`, `il`, `in`, `it`, `jp`, `kr`, `mx`, `my`, `ng`, `nl`, `no`, `ph`, `ru`, `sa`, `sg`, `th`, `tr`, `tw`, `ua`, `us`, `ve`, `za`

## License

MIT
