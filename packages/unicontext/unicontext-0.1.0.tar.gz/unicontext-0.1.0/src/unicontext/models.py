from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Scope:
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    thread_id: Optional[str] = None
    run_id: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class MemoryInput:
    text: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None
    metadata: Optional[Dict[str, Any]] = None
    external_id: Optional[str] = None
    source: Optional[str] = None


@dataclass(frozen=True)
class MemoryRecord:
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    scope: Scope = field(default_factory=Scope)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    provider: str = ""
    raw: Any = None


@dataclass(frozen=True)
class SearchQuery:
    query: str
    scope: Optional[Scope] = None
    limit: int = 10
    filters: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class SearchHit:
    record: MemoryRecord
    rank: int
    score: Optional[float] = None


@dataclass(frozen=True)
class ProviderCapabilities:
    supports_threads: bool = False
    supports_graph: bool = False
    supports_agents: bool = False
    supports_streaming: bool = False
    supports_bulk: bool = False
    supports_delete_by_scope: bool = False
