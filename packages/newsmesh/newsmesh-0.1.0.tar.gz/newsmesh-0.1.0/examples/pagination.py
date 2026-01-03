"""Pagination examples for the NewsMesh Python SDK."""

from newsmesh import NewsMeshClient

API_KEY = "your-api-key"
client = NewsMeshClient(API_KEY)


def manual_pagination():
    """Manually paginate through results using cursors."""
    print("=== Manual Pagination ===\n")

    page = 1
    cursor = None
    total_articles = 0

    while True:
        response = client.get_latest(limit=10, cursor=cursor)

        print(f"Page {page}: {len(response)} articles")
        for article in response:
            total_articles += 1
            print(f"  - {article.title[:50]}...")

        # Check if there are more pages
        if not response.has_more:
            break

        cursor = response.next_cursor
        page += 1

        # Limit pages for demo
        if page > 3:
            print("\n(Stopping after 3 pages for demo)")
            break

    print(f"\nTotal articles fetched: {total_articles}")


def auto_pagination():
    """Use the paginate() helper for automatic pagination."""
    print("=== Auto Pagination ===\n")

    count = 0
    for article in client.paginate("get_latest", limit=10):
        count += 1
        print(f"{count}. {article.title[:60]}...")

        # Limit for demo
        if count >= 25:
            print("\n(Stopping after 25 articles for demo)")
            break

    print(f"\nTotal articles fetched: {count}")


def paginate_search_results():
    """Paginate through search results."""
    print("=== Paginate Search Results ===\n")

    count = 0
    for article in client.paginate("search", query="technology", limit=5):
        count += 1
        print(f"{count}. [{article.category}] {article.title[:50]}...")

        if count >= 15:
            break

    print(f"\nTotal search results: {count}")


def paginate_with_filters():
    """Paginate with category and country filters."""
    print("=== Paginate with Filters ===\n")

    count = 0
    for article in client.paginate(
        "get_latest",
        category=["politics", "world"],
        country="us",
        limit=10,
    ):
        count += 1
        print(f"{count}. [{article.category}] {article.title[:50]}...")

        if count >= 20:
            break

    print(f"\nTotal filtered articles: {count}")


if __name__ == "__main__":
    manual_pagination()
    print("\n" + "=" * 50 + "\n")

    auto_pagination()
    print("\n" + "=" * 50 + "\n")

    paginate_search_results()
    print("\n" + "=" * 50 + "\n")

    paginate_with_filters()

    client.close()
