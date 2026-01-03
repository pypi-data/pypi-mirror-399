"""
GLPI Python SDK - HTTP Client

Unified HTTP client with sync and async support using httpx.
Compatible with FastAPI and anyio.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from .exceptions import (
    ConnectionError,
    ForbiddenError,
    ServerError,
    TimeoutError,
    UnauthorizedError,
)


@dataclass
class ClientConfig:
    """HTTP client configuration."""

    timeout: float = 30.0
    """Default request timeout (seconds)."""

    connect_timeout: float = 10.0
    """Connection timeout (seconds)."""

    max_retries: int = 3
    """Maximum number of retries on network error."""

    retry_on_status: tuple[int, ...] = (502, 503, 504)
    """Status codes that should trigger automatic retry."""

    verify_ssl: bool = True
    """Verify SSL certificates."""

    follow_redirects: bool = True
    """Follow redirects automatically."""

    http2: bool = False
    """Use HTTP/2 when available."""


class BaseHTTPClient:
    """Base class with shared functionality between sync and async."""

    def __init__(self, config: ClientConfig | None = None):
        self.config = config or ClientConfig()
        self._headers: dict[str, str] = {}

    @property
    def timeout(self) -> httpx.Timeout:
        return httpx.Timeout(timeout=self.config.timeout, connect=self.config.connect_timeout)

    def set_headers(self, headers: dict[str, str]) -> None:
        """Set global headers for all requests."""
        self._headers.update(headers)

    def clear_headers(self) -> None:
        """Clear all headers."""
        self._headers.clear()

    def _handle_response_status(self, response: httpx.Response) -> httpx.Response:
        """Check response status and raise appropriate exceptions."""
        if response.status_code == 401:
            raise UnauthorizedError(details=self._safe_json(response))
        elif response.status_code == 403:
            raise ForbiddenError(details=self._safe_json(response))
        elif response.status_code >= 500:
            raise ServerError(status_code=response.status_code, details=self._safe_json(response))
        return response

    @staticmethod
    def _safe_json(response: httpx.Response) -> Any:
        """Try to extract JSON from response, return None on failure."""
        try:
            return response.json()
        except Exception:
            return response.text or None


class HTTPClient(BaseHTTPClient):
    """Synchronous HTTP client using httpx."""

    def __init__(self, config: ClientConfig | None = None):
        super().__init__(config)
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        """Lazy initialization of the client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                timeout=self.timeout,
                verify=self.config.verify_ssl,
                follow_redirects=self.config.follow_redirects,
                http2=self.config.http2,
            )
        return self._client

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None and not self._client.is_closed:
            self._client.close()
            self._client = None

    def __enter__(self) -> HTTPClient:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __del__(self) -> None:
        self.close()

    def request(
        self,
        method: str,
        url: str,
        *,
        params: dict | None = None,
        json: dict | None = None,
        data: dict | None = None,
        files: dict | None = None,
        headers: dict | None = None,
        timeout: float | None = None,
        **kwargs,
    ) -> httpx.Response:
        """Execute an HTTP request."""
        merged_headers = {**self._headers, **(headers or {})}
        request_timeout = httpx.Timeout(timeout) if timeout else self.timeout

        try:
            response = self.client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                data=data,
                files=files,
                headers=merged_headers,
                timeout=request_timeout,
                **kwargs,
            )
            return self._handle_response_status(response)
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to {url}", details=str(e))
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request to {url} timed out", details=str(e))

    def get(self, url: str, **kwargs) -> httpx.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> httpx.Response:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs) -> httpx.Response:
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs) -> httpx.Response:
        return self.request("DELETE", url, **kwargs)

    def patch(self, url: str, **kwargs) -> httpx.Response:
        return self.request("PATCH", url, **kwargs)


class AsyncHTTPClient(BaseHTTPClient):
    """Asynchronous HTTP client using httpx."""

    def __init__(self, config: ClientConfig | None = None):
        super().__init__(config)
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy initialization of the async client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                verify=self.config.verify_ssl,
                follow_redirects=self.config.follow_redirects,
                http2=self.config.http2,
            )
        return self._client

    async def close(self) -> None:
        """Close the async HTTP client."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> AsyncHTTPClient:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: dict | None = None,
        json: dict | None = None,
        data: dict | None = None,
        files: dict | None = None,
        headers: dict | None = None,
        timeout: float | None = None,
        **kwargs,
    ) -> httpx.Response:
        """Execute an async HTTP request."""
        merged_headers = {**self._headers, **(headers or {})}
        request_timeout = httpx.Timeout(timeout) if timeout else self.timeout

        try:
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                data=data,
                files=files,
                headers=merged_headers,
                timeout=request_timeout,
                **kwargs,
            )
            return self._handle_response_status(response)
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to {url}", details=str(e))
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request to {url} timed out", details=str(e))

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("DELETE", url, **kwargs)

    async def patch(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("PATCH", url, **kwargs)


# Union type for type hints
AnyHTTPClient = HTTPClient | AsyncHTTPClient
