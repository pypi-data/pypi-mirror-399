"""HTTP transport layer for the NewsMesh SDK."""

import random
import time
from typing import Any, Dict, Optional

import requests

from .exceptions import (
    NewsMeshError,
    RateLimitError,
    ServerError,
    raise_for_error,
)


DEFAULT_BASE_URL = "https://api.newsmesh.co/v1"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_STATUSES = {429, 500, 502, 503, 504}


class HTTPClient:
    """Synchronous HTTP client with retry logic.

    Handles making HTTP requests to the NewsMesh API with automatic
    retries on transient failures using exponential backoff.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._session: Optional[requests.Session] = None

    @property
    def session(self) -> requests.Session:
        """Lazy-initialize the requests session."""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                "User-Agent": "newsmesh-python/0.1.0",
                "Accept": "application/json",
            })
        return self._session

    def close(self) -> None:
        """Close the HTTP session."""
        if self._session is not None:
            self._session.close()
            self._session = None

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request with automatic retries.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: API endpoint path (e.g., "/trending").
            params: Query parameters to include.

        Returns:
            The JSON response as a dictionary.

        Raises:
            NewsMeshError: On API errors or after max retries exhausted.
        """
        url = f"{self.base_url}{path}"

        # Always include API key in params
        if params is None:
            params = {}
        params["apiKey"] = self.api_key

        last_exception: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    timeout=self.timeout,
                )

                # Parse response JSON
                try:
                    data = response.json()
                except ValueError:
                    data = {}

                # Check for API errors
                if response.status_code >= 400:
                    # Check if we should retry
                    if (
                        response.status_code in DEFAULT_RETRY_STATUSES
                        and attempt < self.max_retries
                    ):
                        self._wait_for_retry(attempt, response)
                        continue

                    # Raise appropriate exception
                    if data.get("status") == "error":
                        raise_for_error(data, response.status_code)
                    else:
                        # Generic error
                        if response.status_code == 429:
                            raise RateLimitError(
                                "Rate limit exceeded",
                                status_code=response.status_code,
                            )
                        elif response.status_code >= 500:
                            raise ServerError(
                                f"Server error: {response.status_code}",
                                status_code=response.status_code,
                            )
                        else:
                            raise NewsMeshError(
                                f"HTTP error: {response.status_code}",
                                status_code=response.status_code,
                            )

                return data

            except requests.exceptions.Timeout as e:
                last_exception = e
                if attempt < self.max_retries:
                    self._wait_for_retry(attempt)
                    continue
                raise NewsMeshError(f"Request timed out after {self.timeout}s") from e

            except requests.exceptions.ConnectionError as e:
                last_exception = e
                if attempt < self.max_retries:
                    self._wait_for_retry(attempt)
                    continue
                raise NewsMeshError("Connection error") from e

            except NewsMeshError:
                raise

            except Exception as e:
                last_exception = e
                raise NewsMeshError(f"Unexpected error: {e}") from e

        # Should not reach here, but just in case
        raise NewsMeshError(
            f"Max retries ({self.max_retries}) exceeded"
        ) from last_exception

    def _wait_for_retry(
        self,
        attempt: int,
        response: Optional[requests.Response] = None,
    ) -> None:
        """Wait before retrying with exponential backoff and jitter.

        Args:
            attempt: The current attempt number (0-indexed).
            response: Optional response to check for Retry-After header.
        """
        # Check for Retry-After header
        if response is not None:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    wait_time = float(retry_after)
                    time.sleep(wait_time)
                    return
                except ValueError:
                    pass

        # Exponential backoff with jitter: 0.5s, 1s, 2s, 4s...
        base_wait = 0.5 * (2 ** attempt)
        jitter = random.uniform(0, 0.5 * base_wait)
        time.sleep(base_wait + jitter)

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a GET request.

        Args:
            path: API endpoint path.
            params: Query parameters.

        Returns:
            The JSON response as a dictionary.
        """
        return self.request("GET", path, params)
