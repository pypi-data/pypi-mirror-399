"""Tests for NewsMesh SDK models."""

import pytest
from datetime import datetime

from newsmesh.models import Article, PaginatedResponse


class TestArticle:
    """Tests for the Article model."""

    def test_from_dict(self, sample_article_data):
        """Test creating Article from dict."""
        article = Article.from_dict(sample_article_data)

        assert article.article_id == "abc123"
        assert article.title == "Test Article Title"
        assert article.description == "This is a test article description."
        assert article.link == "https://example.com/article"
        assert article.published_date == "2025-01-15T10:30:00Z"
        assert article.source == "Test Source"
        assert article.category == "technology"
        assert article.topics == ["tech", "news"]
        assert article.media_url == "https://example.com/image.jpg"
        assert article.people == ["John Doe"]
        assert article.author == "Jane Smith"

    def test_from_dict_minimal(self):
        """Test creating Article with minimal data."""
        data = {
            "article_id": "xyz789",
            "title": "Minimal Article",
            "description": "Description",
            "link": "https://example.com",
            "published_date": "2025-01-15T10:30:00Z",
            "source": "Source",
            "category": "news",
        }
        article = Article.from_dict(data)

        assert article.article_id == "xyz789"
        assert article.topics == []
        assert article.media_url is None
        assert article.people is None
        assert article.author is None

    def test_published_datetime(self, sample_article_data):
        """Test parsing published_date as datetime."""
        article = Article.from_dict(sample_article_data)
        dt = article.published_datetime

        assert isinstance(dt, datetime)
        assert dt.year == 2025
        assert dt.month == 1
        assert dt.day == 15
        assert dt.hour == 10
        assert dt.minute == 30


class TestPaginatedResponse:
    """Tests for the PaginatedResponse model."""

    def test_from_dict(self, sample_response, sample_article_data):
        """Test creating PaginatedResponse from dict."""
        response = PaginatedResponse.from_dict(sample_response)

        assert len(response.data) == 1
        assert response.next_cursor is not None
        assert response.has_more is True

    def test_from_dict_no_cursor(self, sample_article_data):
        """Test response without next_cursor."""
        data = {"data": [sample_article_data], "next_cursor": None}
        response = PaginatedResponse.from_dict(data)

        assert response.next_cursor is None
        assert response.has_more is False

    def test_iteration(self, sample_response):
        """Test iterating over response."""
        response = PaginatedResponse.from_dict(sample_response)

        articles = list(response)
        assert len(articles) == 1
        assert isinstance(articles[0], Article)

    def test_len(self, sample_response):
        """Test len() on response."""
        response = PaginatedResponse.from_dict(sample_response)
        assert len(response) == 1

    def test_bool_true(self, sample_response):
        """Test bool() with articles."""
        response = PaginatedResponse.from_dict(sample_response)
        assert bool(response) is True

    def test_bool_false(self):
        """Test bool() without articles."""
        response = PaginatedResponse.from_dict({"data": [], "next_cursor": None})
        assert bool(response) is False

    def test_empty_response(self):
        """Test empty response."""
        response = PaginatedResponse.from_dict({"data": []})

        assert len(response) == 0
        assert response.next_cursor is None
        assert response.has_more is False
