"""Async usage examples for the NewsMesh Python SDK."""

import asyncio

from newsmesh import AsyncNewsMeshClient

API_KEY = "your-api-key"


async def example_trending():
    """Get trending articles asynchronously."""
    print("=== Trending Articles (Async) ===\n")

    async with AsyncNewsMeshClient(API_KEY) as client:
        response = await client.get_trending(limit=5)

        for article in response:
            print(f"Title: {article.title}")
            print(f"Source: {article.source}")
            print()


async def example_concurrent_requests():
    """Make multiple requests concurrently."""
    print("=== Concurrent Requests ===\n")

    async with AsyncNewsMeshClient(API_KEY) as client:
        # Run multiple requests concurrently
        trending_task = client.get_trending(limit=3)
        latest_task = client.get_latest(limit=3)
        search_task = client.search("technology", limit=3)

        trending, latest, search_results = await asyncio.gather(
            trending_task,
            latest_task,
            search_task,
        )

        print(f"Trending: {len(trending)} articles")
        print(f"Latest: {len(latest)} articles")
        print(f"Search: {len(search_results)} articles")


async def example_pagination():
    """Paginate through results asynchronously."""
    print("=== Async Pagination ===\n")

    async with AsyncNewsMeshClient(API_KEY) as client:
        count = 0
        async for article in client.paginate("get_latest", limit=10):
            print(f"{count + 1}. {article.title}")
            count += 1
            if count >= 20:  # Limit to 20 articles for demo
                break

        print(f"\nTotal articles fetched: {count}")


async def main():
    """Run all examples."""
    await example_trending()
    print("\n" + "=" * 50 + "\n")

    await example_concurrent_requests()
    print("\n" + "=" * 50 + "\n")

    await example_pagination()


if __name__ == "__main__":
    asyncio.run(main())
