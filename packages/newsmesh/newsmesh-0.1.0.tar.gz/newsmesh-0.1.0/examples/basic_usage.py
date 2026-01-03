"""Basic usage examples for the NewsMesh Python SDK."""

from newsmesh import NewsMeshClient

# Initialize the client
API_KEY = "your-api-key"
client = NewsMeshClient(API_KEY)


def example_trending():
    """Get trending articles."""
    print("=== Trending Articles ===\n")

    response = client.get_trending(limit=5)

    for article in response:
        print(f"Title: {article.title}")
        print(f"Source: {article.source}")
        print(f"Category: {article.category}")
        print(f"Link: {article.link}")
        print()


def example_latest():
    """Get latest articles with filters."""
    print("=== Latest Tech Articles (US) ===\n")

    response = client.get_latest(
        category="technology",
        country="us",
        limit=5,
    )

    for article in response:
        print(f"Title: {article.title}")
        print(f"Published: {article.published_date}")
        print()


def example_search():
    """Search for articles."""
    print("=== Search Results for 'climate' ===\n")

    response = client.search(
        "climate",
        limit=5,
        sort_by="relevant",
    )

    for article in response:
        print(f"Title: {article.title}")
        print(f"Description: {article.description[:100]}...")
        print()


def example_single_article():
    """Get a specific article by ID."""
    print("=== Single Article ===\n")

    # First, get an article ID from trending
    trending = client.get_trending(limit=1)
    if trending.data:
        article_id = trending.data[0].article_id
        article = client.get_article(article_id)

        print(f"Title: {article.title}")
        print(f"Source: {article.source}")
        print(f"Category: {article.category}")
        print(f"Topics: {', '.join(article.topics)}")
        if article.author:
            print(f"Author: {article.author}")
        print(f"Link: {article.link}")


def example_error_handling():
    """Demonstrate error handling."""
    from newsmesh import NotFoundError, ValidationError

    print("=== Error Handling ===\n")

    # Handle not found
    try:
        client.get_article("non-existent-article-id")
    except NotFoundError as e:
        print(f"Article not found: {e.message}")

    # Handle validation error
    try:
        client.search("")  # Empty query
    except ValidationError as e:
        print(f"Validation error: {e.message}")


if __name__ == "__main__":
    example_trending()
    print("\n" + "=" * 50 + "\n")

    example_latest()
    print("\n" + "=" * 50 + "\n")

    example_search()
    print("\n" + "=" * 50 + "\n")

    example_single_article()
    print("\n" + "=" * 50 + "\n")

    example_error_handling()

    # Clean up
    client.close()
