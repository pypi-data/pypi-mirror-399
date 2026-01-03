from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .client import ContextClient
from .exceptions import ValidationError
from .provider import Provider
from .providers.mem0 import Mem0Provider
from .providers.supermemory import SupermemoryProvider
from .providers.zep import ZepProvider
from .providers.letta import LettaProvider


@dataclass(frozen=True)
class ProviderConfig:
    provider: str
    api_key: str
    base_url: Optional[str] = None
    timeout_s: float = 30.0
    extra: Dict[str, Any] | None = None


def create_provider(config: ProviderConfig) -> Provider:
    provider = config.provider.strip().lower()
    if not provider:
        raise ValidationError(
            "provider is required", provider="(factory)", operation="create_provider"
        )
    if not config.api_key:
        raise ValidationError(
            "api_key is required",
            provider=provider,
            operation="create_provider",
        )

    extra = config.extra or {}

    if provider == "mem0":
        return Mem0Provider(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout_s=config.timeout_s,
            extra=extra,
        )
    if provider == "supermemory":
        return SupermemoryProvider(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout_s=config.timeout_s,
            extra=extra,
        )
    if provider == "zep":
        return ZepProvider(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout_s=config.timeout_s,
            extra=extra,
        )
    if provider == "letta":
        return LettaProvider(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout_s=config.timeout_s,
            extra=extra,
        )

    raise ValidationError(
        f"Unknown provider: {config.provider}. Supported: mem0, supermemory, zep, letta",
        provider=provider,
        operation="create_provider",
    )


def create_client(
    provider: str,
    api_key: str,
    base_url: Optional[str] = None,
    timeout_s: float = 30.0,
    extra: Optional[Dict[str, Any]] = None,
) -> ContextClient:
    cfg = ProviderConfig(
        provider=provider,
        api_key=api_key,
        base_url=base_url,
        timeout_s=timeout_s,
        extra=extra,
    )
    return ContextClient(provider=create_provider(cfg))
