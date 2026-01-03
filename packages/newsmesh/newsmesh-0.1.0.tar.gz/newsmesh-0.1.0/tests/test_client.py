"""Tests for NewsMesh sync client."""

import pytest
import responses

from newsmesh import NewsMeshClient
from newsmesh.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


class TestNewsMeshClient:
    """Tests for NewsMeshClient."""

    def test_init_requires_api_key(self):
        """Test that client requires API key."""
        with pytest.raises(ValueError, match="api_key is required"):
            NewsMeshClient("")

    def test_init_with_api_key(self, api_key):
        """Test client initialization."""
        client = NewsMeshClient(api_key)
        assert client._http.api_key == api_key
        client.close()

    def test_context_manager(self, api_key):
        """Test client as context manager."""
        with NewsMeshClient(api_key) as client:
            assert client._http.api_key == api_key

    @responses.activate
    def test_get_trending(self, api_key, sample_response):
        """Test get_trending method."""
        responses.add(
            responses.GET,
            "https://api.newsmesh.co/v1/trending",
            json=sample_response,
            status=200,
        )

        client = NewsMeshClient(api_key)
        response = client.get_trending(limit=10)

        assert len(response) == 1
        assert response.data[0].title == "Test Article Title"
        client.close()

    @responses.activate
    def test_get_latest(self, api_key, sample_response):
        """Test get_latest method."""
        responses.add(
            responses.GET,
            "https://api.newsmesh.co/v1/latest",
            json=sample_response,
            status=200,
        )

        client = NewsMeshClient(api_key)
        response = client.get_latest(category="technology", country="us")

        assert len(response) == 1
        client.close()

    @responses.activate
    def test_get_latest_with_list_params(self, api_key, sample_response):
        """Test get_latest with list parameters."""
        responses.add(
            responses.GET,
            "https://api.newsmesh.co/v1/latest",
            json=sample_response,
            status=200,
        )

        client = NewsMeshClient(api_key)
        response = client.get_latest(
            category=["politics", "world"],
            country=["us", "gb"],
        )

        # Check that params were formatted correctly
        request = responses.calls[0].request
        assert "category=politics%2Cworld" in request.url or "category=politics,world" in request.url
        client.close()

    @responses.activate
    def test_get_article(self, api_key, sample_article_data):
        """Test get_article method."""
        responses.add(
            responses.GET,
            "https://api.newsmesh.co/v1/article/abc123",
            json={"data": [sample_article_data]},
            status=200,
        )

        client = NewsMeshClient(api_key)
        article = client.get_article("abc123")

        assert article.article_id == "abc123"
        assert article.title == "Test Article Title"
        client.close()

    def test_get_article_empty_id(self, api_key):
        """Test get_article with empty ID."""
        client = NewsMeshClient(api_key)
        with pytest.raises(ValueError, match="article_id is required"):
            client.get_article("")
        client.close()

    @responses.activate
    def test_search(self, api_key, sample_response):
        """Test search method."""
        responses.add(
            responses.GET,
            "https://api.newsmesh.co/v1/search",
            json=sample_response,
            status=200,
        )

        client = NewsMeshClient(api_key)
        response = client.search("technology", limit=10, sort_by="relevant")

        assert len(response) == 1
        client.close()

    def test_search_empty_query(self, api_key):
        """Test search with empty query."""
        client = NewsMeshClient(api_key)
        with pytest.raises(ValidationError):
            client.search("")
        client.close()

    def test_search_query_too_long(self, api_key):
        """Test search with query > 500 chars."""
        client = NewsMeshClient(api_key)
        with pytest.raises(ValidationError):
            client.search("x" * 501)
        client.close()

    @responses.activate
    def test_authentication_error(self, api_key, sample_error_response):
        """Test handling of authentication error."""
        responses.add(
            responses.GET,
            "https://api.newsmesh.co/v1/trending",
            json=sample_error_response,
            status=401,
        )

        client = NewsMeshClient(api_key)
        with pytest.raises(AuthenticationError):
            client.get_trending()
        client.close()

    @responses.activate
    def test_rate_limit_error(self, api_key):
        """Test handling of rate limit error."""
        responses.add(
            responses.GET,
            "https://api.newsmesh.co/v1/trending",
            json={
                "status": "error",
                "code": "dailyLimitExceeded",
                "message": "Daily limit exceeded",
            },
            status=429,
        )

        client = NewsMeshClient(api_key, max_retries=0)
        with pytest.raises(RateLimitError):
            client.get_trending()
        client.close()

    @responses.activate
    def test_not_found_error(self, api_key):
        """Test handling of not found error."""
        responses.add(
            responses.GET,
            "https://api.newsmesh.co/v1/article/invalid",
            json={
                "status": "error",
                "code": "articleNotFound",
                "message": "Article not found",
            },
            status=404,
        )

        client = NewsMeshClient(api_key)
        with pytest.raises(NotFoundError):
            client.get_article("invalid")
        client.close()

    def test_paginate_invalid_method(self, api_key):
        """Test paginate with invalid method."""
        client = NewsMeshClient(api_key)
        with pytest.raises(ValueError):
            list(client.paginate("get_trending"))
        with pytest.raises(ValueError):
            list(client.paginate("invalid_method"))
        client.close()

    @responses.activate
    def test_paginate(self, api_key, sample_article_data):
        """Test pagination helper."""
        # First page with cursor
        responses.add(
            responses.GET,
            "https://api.newsmesh.co/v1/latest",
            json={
                "data": [sample_article_data],
                "next_cursor": "cursor123",
            },
            status=200,
        )
        # Second page without cursor (last page)
        responses.add(
            responses.GET,
            "https://api.newsmesh.co/v1/latest",
            json={
                "data": [sample_article_data],
                "next_cursor": None,
            },
            status=200,
        )

        client = NewsMeshClient(api_key)
        articles = list(client.paginate("get_latest", limit=1))

        assert len(articles) == 2
        assert len(responses.calls) == 2
        client.close()

    @responses.activate
    def test_limit_clamping(self, api_key, sample_response):
        """Test that limit is clamped to valid range."""
        responses.add(
            responses.GET,
            "https://api.newsmesh.co/v1/trending",
            json=sample_response,
            status=200,
        )

        client = NewsMeshClient(api_key)
        client.get_trending(limit=100)  # Should be clamped to 25

        request = responses.calls[0].request
        assert "limit=25" in request.url
        client.close()

    @responses.activate
    def test_date_formatting(self, api_key, sample_response):
        """Test date parameter formatting."""
        from datetime import date

        responses.add(
            responses.GET,
            "https://api.newsmesh.co/v1/latest",
            json=sample_response,
            status=200,
        )

        client = NewsMeshClient(api_key)
        client.get_latest(from_date=date(2025, 1, 15))

        request = responses.calls[0].request
        assert "from=2025-01-15" in request.url
        client.close()
