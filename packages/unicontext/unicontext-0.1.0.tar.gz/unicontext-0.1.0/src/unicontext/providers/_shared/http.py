"""
HTTP-first shared transport layer for all provider adapters.

Provides:
- Retry + exponential backoff (429/5xx)
- Auth injection (Token, Bearer, Api-Key)
- Timeout management
- Error normalization
- JSON utilities
"""

from __future__ import annotations

import time
import random
from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional

import httpx

from ...exceptions import (
    AuthError,
    NotFoundError,
    ProviderError,
    RateLimitError,
    TransientError,
    ValidationError,
)


def _get_version() -> str:
    """Get package version dynamically."""
    try:
        from ..._version import __version__

        return __version__
    except ImportError:
        return "0.1.0"


USER_AGENT = f"unicontext/{_get_version()} (HTTP-first)"


AuthStyle = Literal["token", "bearer", "api-key"]


@dataclass
class HTTPConfig:
    """Configuration for the shared HTTP transport."""

    base_url: str
    auth_header: str  # full header value, e.g. "Bearer xxx" or "Token xxx"
    timeout_s: float = 30.0
    max_retries: int = 3
    backoff_base: float = 1.0  # base seconds for exponential backoff
    backoff_max: float = 30.0  # max seconds for backoff
    headers: Dict[str, str] = field(default_factory=dict)


def build_auth_header(api_key: str, style: AuthStyle) -> str:
    """Build the Authorization header value based on auth style."""
    if style == "token":
        return f"Token {api_key}"
    elif style == "bearer":
        return f"Bearer {api_key}"
    elif style == "api-key":
        return f"Api-Key {api_key}"
    else:
        return f"Bearer {api_key}"


def raise_for_status(
    *,
    provider: str,
    operation: str,
    response: httpx.Response,
    raw: Any,
) -> None:
    """Map HTTP status codes to library exceptions."""
    status = response.status_code
    if 200 <= status < 300:
        return

    # Try to extract error message from response
    message = "Provider request failed"
    if isinstance(raw, dict):
        message = raw.get("message") or raw.get("error") or raw.get("detail") or message
    elif isinstance(raw, str) and raw:
        message = raw[:500]

    if status == 400:
        raise ValidationError(
            message, provider=provider, operation=operation, status_code=status, raw=raw
        )
    if status in (401, 403):
        raise AuthError(
            message, provider=provider, operation=operation, status_code=status, raw=raw
        )
    if status == 404:
        raise NotFoundError(
            message, provider=provider, operation=operation, status_code=status, raw=raw
        )
    if status == 429:
        raise RateLimitError(
            message, provider=provider, operation=operation, status_code=status, raw=raw
        )
    if 500 <= status <= 599:
        raise TransientError(
            message, provider=provider, operation=operation, status_code=status, raw=raw
        )

    raise ProviderError(
        message, provider=provider, operation=operation, status_code=status, raw=raw
    )


def maybe_json(response: httpx.Response) -> Any:
    """Safely parse JSON from response, fallback to text."""
    try:
        return response.json()
    except Exception:
        return response.text


def join_messages(messages: list[dict[str, str]]) -> str:
    """Join a list of chat messages into a single text string."""
    parts: list[str] = []
    for m in messages:
        role = m.get("role", "")
        content = m.get("content", "")
        parts.append(f"{role}: {content}".strip())
    return "\n".join(parts)


def http_client(timeout_s: float) -> httpx.Client:
    """Create a basic httpx Client with timeout."""
    return httpx.Client(timeout=httpx.Timeout(timeout_s))


class HTTPTransport:
    """
    Shared HTTP transport with retry, backoff, auth injection.

    Usage:
        transport = HTTPTransport(config)
        response = transport.request("POST", "/v1/memories/", json=payload)
    """

    def __init__(self, config: HTTPConfig, provider: str):
        self.config = config
        self.provider = provider
        self._client: Optional[httpx.Client] = None

    def _get_client(self) -> httpx.Client:
        if self._client is None or self._client.is_closed:
            headers = {
                "Authorization": self.config.auth_header,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            }
            headers.update(self.config.headers)
            self._client = httpx.Client(
                base_url=self.config.base_url,
                headers=headers,
                timeout=httpx.Timeout(self.config.timeout_s),
            )
        return self._client

    def close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            self._client.close()
            self._client = None

    def _should_retry(self, status: int) -> bool:
        """Determine if request should be retried based on status code."""
        return status == 429 or (500 <= status <= 599)

    def _calculate_backoff(self, attempt: int, response: Optional[httpx.Response] = None) -> float:
        """Calculate backoff time with jitter."""
        # Check for Retry-After header
        if response is not None:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    return min(float(retry_after), self.config.backoff_max)
                except ValueError:
                    pass

        # Exponential backoff with jitter
        backoff = min(
            self.config.backoff_base * (2**attempt) + random.uniform(0, 1), self.config.backoff_max
        )
        return backoff

    def request(
        self,
        method: str,
        path: str,
        operation: str,
        *,
        json: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Make an HTTP request with retry and error handling.

        Returns parsed JSON response on success.
        Raises appropriate library exceptions on failure.
        """
        client = self._get_client()

        last_exception: Optional[Exception] = None
        last_response: Optional[httpx.Response] = None

        for attempt in range(self.config.max_retries + 1):
            try:
                kwargs: Dict[str, Any] = {}
                if json is not None:
                    kwargs["json"] = json
                if params is not None:
                    kwargs["params"] = params
                if data is not None:
                    kwargs["data"] = data
                if extra_headers:
                    kwargs["headers"] = extra_headers

                response = client.request(method, path, **kwargs)
                last_response = response
                raw = maybe_json(response)

                # Success - return immediately
                if 200 <= response.status_code < 300:
                    return raw

                # Check if retryable
                if self._should_retry(response.status_code) and attempt < self.config.max_retries:
                    backoff = self._calculate_backoff(attempt, response)
                    time.sleep(backoff)
                    continue

                # Non-retryable error or exhausted retries
                raise_for_status(
                    provider=self.provider,
                    operation=operation,
                    response=response,
                    raw=raw,
                )

            except (
                httpx.ConnectError,
                httpx.ReadTimeout,
                httpx.WriteTimeout,
                httpx.PoolTimeout,
            ) as e:
                last_exception = e
                if attempt < self.config.max_retries:
                    backoff = self._calculate_backoff(attempt)
                    time.sleep(backoff)
                    continue
                raise TransientError(
                    f"Connection error: {str(e)}",
                    provider=self.provider,
                    operation=operation,
                    raw=str(e),
                )
            except (
                AuthError,
                NotFoundError,
                ValidationError,
                RateLimitError,
                TransientError,
                ProviderError,
            ):
                # Re-raise our own exceptions
                raise
            except Exception as e:
                last_exception = e
                raise ProviderError(
                    f"Unexpected error: {str(e)}",
                    provider=self.provider,
                    operation=operation,
                    raw=str(e),
                )

        # Should not reach here, but just in case
        if last_response is not None:
            raise_for_status(
                provider=self.provider,
                operation=operation,
                response=last_response,
                raw=maybe_json(last_response),
            )
        raise ProviderError(
            f"Request failed after {self.config.max_retries} retries",
            provider=self.provider,
            operation=operation,
            raw=str(last_exception),
        )

    def get(self, path: str, operation: str, *, params: Optional[Dict[str, Any]] = None) -> Any:
        """Convenience method for GET requests."""
        return self.request("GET", path, operation, params=params)

    def post(
        self,
        path: str,
        operation: str,
        *,
        json: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Convenience method for POST requests."""
        return self.request("POST", path, operation, json=json, params=params)

    def delete(self, path: str, operation: str, *, params: Optional[Dict[str, Any]] = None) -> Any:
        """Convenience method for DELETE requests."""
        return self.request("DELETE", path, operation, params=params)

    def put(self, path: str, operation: str, *, json: Optional[Any] = None) -> Any:
        """Convenience method for PUT requests."""
        return self.request("PUT", path, operation, json=json)

    def patch(self, path: str, operation: str, *, json: Optional[Any] = None) -> Any:
        """Convenience method for PATCH requests."""
        return self.request("PATCH", path, operation, json=json)
