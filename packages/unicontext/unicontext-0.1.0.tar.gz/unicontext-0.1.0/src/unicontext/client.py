from __future__ import annotations

from typing import Optional

from .exceptions import ValidationError
from .models import MemoryInput, MemoryRecord, ProviderCapabilities, Scope, SearchHit, SearchQuery
from .provider import Provider


def _validate_input(provider: str, operation: str, input: MemoryInput) -> None:
    has_text = input.text is not None and input.text.strip() != ""
    has_messages = input.messages is not None and len(input.messages) > 0

    if not has_text and not has_messages:
        raise ValidationError(
            "Provide either `text` (non-empty) or `messages` (non-empty list).",
            provider=provider,
            operation=operation,
        )

    if has_text and has_messages:
        raise ValidationError(
            "Provide exactly one of `text` or `messages`, not both.",
            provider=provider,
            operation=operation,
        )


def _validate_search_query(provider: str, query: SearchQuery) -> None:
    if not query.query or not query.query.strip():
        raise ValidationError(
            "SearchQuery.query must be a non-empty string.",
            provider=provider,
            operation="search",
        )
    if query.limit is not None and query.limit < 1:
        raise ValidationError(
            "SearchQuery.limit must be a positive integer.",
            provider=provider,
            operation="search",
        )


def _validate_memory_id(provider: str, operation: str, memory_id: str) -> None:
    if not memory_id or not memory_id.strip():
        raise ValidationError(
            "memory_id must be a non-empty string.",
            provider=provider,
            operation=operation,
        )


class ContextClient:
    def __init__(self, provider: Provider):
        self._provider = provider

    @property
    def provider_name(self) -> str:
        return self._provider.name

    def capabilities(self) -> ProviderCapabilities:
        return self._provider.capabilities()

    def add(self, input: MemoryInput, scope: Scope) -> MemoryRecord:
        _validate_input(self.provider_name, "add", input)
        return self._provider.add(input=input, scope=scope)

    def search(self, query: SearchQuery) -> list[SearchHit]:
        _validate_search_query(self.provider_name, query)
        return self._provider.search(query=query)

    def get(self, memory_id: str, scope: Optional[Scope] = None) -> MemoryRecord:
        _validate_memory_id(self.provider_name, "get", memory_id)
        return self._provider.get(memory_id=memory_id, scope=scope)

    def delete(self, memory_id: str, scope: Optional[Scope] = None) -> None:
        _validate_memory_id(self.provider_name, "delete", memory_id)
        self._provider.delete(memory_id=memory_id, scope=scope)

    def delete_by_scope(self, scope: Scope) -> int:
        return self._provider.delete_by_scope(scope=scope)

    def with_provider(self, provider: Provider) -> "ContextClient":
        return ContextClient(provider=provider)


class AsyncContextClient:
    """Async entry point placeholder.

    We will add async providers one-by-one. For now, this exists so the public
    API is stable, even if it raises NotImplementedError until implemented.
    """

    def __init__(self, provider: Provider):
        self._provider = provider

    @property
    def provider_name(self) -> str:
        return self._provider.name

    def capabilities(self) -> ProviderCapabilities:
        return self._provider.capabilities()

    async def add(self, input: MemoryInput, scope: Scope) -> MemoryRecord:
        _validate_input(self.provider_name, "add", input)
        raise NotImplementedError("Async providers not implemented yet")

    async def search(self, query: SearchQuery) -> list[SearchHit]:
        _validate_search_query(self.provider_name, query)
        raise NotImplementedError("Async providers not implemented yet")

    async def get(self, memory_id: str, scope: Optional[Scope] = None) -> MemoryRecord:
        _validate_memory_id(self.provider_name, "get", memory_id)
        raise NotImplementedError("Async providers not implemented yet")

    async def delete(self, memory_id: str, scope: Optional[Scope] = None) -> None:
        _validate_memory_id(self.provider_name, "delete", memory_id)
        raise NotImplementedError("Async providers not implemented yet")

    async def delete_by_scope(self, scope: Scope) -> int:
        raise NotImplementedError("Async providers not implemented yet")
