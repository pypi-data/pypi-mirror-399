"""HTTP client wrapper for Anchor SDK."""

import os
from typing import Any, Dict, Optional
import httpx

from anchor.exceptions import (
    AnchorError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


class HTTPClient:
    """HTTP client for Anchor API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.getanchor.dev",
        timeout: float = 30.0,
    ):
        self.api_key = api_key or os.environ.get("ANCHOR_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key required. Pass api_key or set ANCHOR_API_KEY."
            )

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate errors."""
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")

        if response.status_code == 404:
            data = response.json() if response.content else {}
            raise NotFoundError(
                data.get("resource_type", "Resource"),
                data.get("resource_id", "unknown"),
            )

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(retry_after)

        if response.status_code == 422:
            data = response.json() if response.content else {}
            raise ValidationError(
                data.get("message", "Validation error"),
                data.get("field"),
            )

        if response.status_code >= 400:
            data = response.json() if response.content else {}
            raise AnchorError(
                data.get("message", f"API error: {response.status_code}"),
                data.get("code"),
            )

        if response.status_code == 204:
            return {}

        return response.json()

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make GET request."""
        url = f"{self.base_url}{path}"
        response = self._client.get(url, headers=self._headers(), params=params)
        return self._handle_response(response)

    def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make POST request."""
        url = f"{self.base_url}{path}"
        response = self._client.post(url, headers=self._headers(), json=json)
        return self._handle_response(response)

    def put(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make PUT request."""
        url = f"{self.base_url}{path}"
        response = self._client.put(url, headers=self._headers(), json=json)
        return self._handle_response(response)

    def patch(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make PATCH request."""
        url = f"{self.base_url}{path}"
        response = self._client.patch(url, headers=self._headers(), json=json)
        return self._handle_response(response)

    def delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make DELETE request."""
        url = f"{self.base_url}{path}"
        response = self._client.delete(url, headers=self._headers(), params=params)
        return self._handle_response(response)

    def close(self):
        """Close the HTTP client."""
        self._client.close()
