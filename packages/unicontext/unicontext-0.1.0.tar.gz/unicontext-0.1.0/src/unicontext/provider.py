from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from .models import MemoryInput, MemoryRecord, ProviderCapabilities, Scope, SearchHit, SearchQuery


class Provider(ABC):
    """Provider adapter contract.

    This is intentionally minimal. Advanced features should be exposed through
    separate capability objects, not added here.
    """

    name: str

    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        raise NotImplementedError

    @abstractmethod
    def add(self, input: MemoryInput, scope: Scope) -> MemoryRecord:
        raise NotImplementedError

    @abstractmethod
    def search(self, query: SearchQuery) -> list[SearchHit]:
        raise NotImplementedError

    @abstractmethod
    def get(self, memory_id: str, scope: Optional[Scope] = None) -> MemoryRecord:
        raise NotImplementedError

    @abstractmethod
    def delete(self, memory_id: str, scope: Optional[Scope] = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_by_scope(self, scope: Scope) -> int:
        raise NotImplementedError
