from __future__ import annotations

from typing import Any, Optional


class ContextSDKError(Exception):
    def __init__(
        self,
        message: str,
        provider: str,
        operation: str,
        status_code: Optional[int] = None,
        raw: Any = None,
    ):
        self.message = message
        self.provider = provider
        self.operation = operation
        self.status_code = status_code
        self.raw = raw
        super().__init__(message)

    def __str__(self) -> str:
        bits = [self.message, f"provider={self.provider}", f"op={self.operation}"]
        if self.status_code is not None:
            bits.append(f"status={self.status_code}")
        return " | ".join(bits)


class ValidationError(ContextSDKError):
    pass


class AuthError(ContextSDKError):
    pass


class RateLimitError(ContextSDKError):
    pass


class NotFoundError(ContextSDKError):
    pass


class NotSupportedError(ContextSDKError):
    pass


class TransientError(ContextSDKError):
    pass


class ProviderError(ContextSDKError):
    pass
