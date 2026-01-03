"""Pytest fixtures for NewsMesh SDK tests."""

import pytest


@pytest.fixture
def api_key():
    """Test API key."""
    return "test-api-key-12345"


@pytest.fixture
def sample_article_data():
    """Sample article data from API response."""
    return {
        "article_id": "abc123",
        "title": "Test Article Title",
        "description": "This is a test article description.",
        "link": "https://example.com/article",
        "published_date": "2025-01-15T10:30:00Z",
        "source": "Test Source",
        "category": "technology",
        "topics": ["tech", "news"],
        "media_url": "https://example.com/image.jpg",
        "people": ["John Doe"],
        "author": "Jane Smith",
    }


@pytest.fixture
def sample_response(sample_article_data):
    """Sample API response with articles."""
    return {
        "data": [sample_article_data],
        "next_cursor": "eyJwdWJsaXNoZWRfZGF0ZSI6ICIyMDI1LTAxLTE1VDEwOjMwOjAwWiJ9",
    }


@pytest.fixture
def sample_error_response():
    """Sample API error response."""
    return {
        "status": "error",
        "code": "invalidApiKey",
        "message": "The provided API key is invalid.",
    }
