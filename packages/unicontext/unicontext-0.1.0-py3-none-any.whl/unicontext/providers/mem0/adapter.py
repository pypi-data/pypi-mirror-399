"""
Mem0 provider adapter - HTTP-first implementation (no SDK dependency).

Endpoints:
- Add: POST /v1/memories/
- Search: POST /v2/memories/search
- List: POST /v2/memories
- Get: GET /v1/memories/{memory_id}
- Delete: DELETE /v1/memories/{memory_id}

Auth: Authorization: Token <MEM0_API_KEY>
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

from ...exceptions import ValidationError
from ...models import MemoryInput, MemoryRecord, ProviderCapabilities, Scope, SearchHit, SearchQuery
from ...provider import Provider
from .._shared import HTTPConfig, HTTPTransport, build_auth_header, join_messages


DEFAULT_BASE_URL = "https://api.mem0.ai"


@dataclass
class Mem0Provider(Provider):
    """
    Mem0 provider using direct HTTP calls.

    No SDK installation required.
    """

    api_key: str
    base_url: Optional[str] = None
    timeout_s: float = 30.0
    extra: Dict[str, Any] | None = None

    name: str = "mem0"
    _transport: HTTPTransport | None = field(default=None, init=False, repr=False)

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_delete_by_scope=True,
            supports_bulk=False,
        )

    def _get_transport(self) -> HTTPTransport:
        if self._transport is None:
            base = self.base_url or DEFAULT_BASE_URL
            # Build extra headers for org_id, project_id if provided
            headers: Dict[str, str] = {}
            if self.extra:
                if self.extra.get("org_id"):
                    headers["Mem0-Org-Id"] = str(self.extra["org_id"])
                if self.extra.get("project_id"):
                    headers["Mem0-Project-Id"] = str(self.extra["project_id"])

            config = HTTPConfig(
                base_url=base,
                auth_header=build_auth_header(self.api_key, "token"),
                timeout_s=self.timeout_s,
                headers=headers,
            )
            self._transport = HTTPTransport(config, provider=self.name)
        return self._transport

    def _require_user_id(self, scope: Scope, operation: str) -> str:
        if not scope.user_id:
            raise ValidationError(
                "Mem0 requires scope.user_id",
                provider=self.name,
                operation=operation,
            )
        return scope.user_id

    def _build_scope_filters(self, scope: Scope) -> Dict[str, Any]:
        """Build Mem0 filters from Scope."""
        filters: Dict[str, Any] = {}
        if scope.user_id:
            filters["user_id"] = scope.user_id
        if scope.agent_id:
            filters["agent_id"] = scope.agent_id
        if scope.run_id:
            filters["run_id"] = scope.run_id
        return filters

    def add(self, input: MemoryInput, scope: Scope) -> MemoryRecord:
        """
        Add a memory to Mem0.

        Note: Mem0 processes memories asynchronously. The returned ID is an event_id
        that may not be immediately usable for get() or delete() operations.
        """
        user_id = self._require_user_id(scope, "add")
        transport = self._get_transport()

        messages = input.messages
        if messages is None:
            messages = [{"role": "user", "content": input.text or ""}]

        metadata: Dict[str, Any] = {}
        if input.metadata:
            metadata.update(input.metadata)
        if input.external_id:
            metadata["_unicontext_external_id"] = input.external_id
        if input.source:
            metadata["_unicontext_source"] = input.source

        payload: Dict[str, Any] = {
            "messages": messages,
            "user_id": user_id,
        }
        if metadata:
            payload["metadata"] = metadata
        if scope.agent_id:
            payload["agent_id"] = scope.agent_id
        if scope.run_id:
            payload["run_id"] = scope.run_id

        res = transport.post("/v1/memories/", "add", json=payload)

        memory_id: str = "unknown"
        is_pending = False

        if isinstance(res, dict):
            results = res.get("results", [])
            if isinstance(results, list) and len(results) > 0:
                first_result = results[0]
                if isinstance(first_result, dict):
                    memory_id = str(
                        first_result.get("event_id") or first_result.get("id") or "unknown"
                    )
                    is_pending = first_result.get("status") == "PENDING"
            if memory_id == "unknown":
                memory_id = str(
                    res.get("id") or res.get("memory_id") or res.get("event_id") or "unknown"
                )

        if is_pending:
            metadata["_mem0_event_id"] = memory_id
            metadata["_mem0_status"] = "PENDING"

        content = join_messages(messages)
        return MemoryRecord(
            id=memory_id,
            content=content,
            metadata=metadata,
            scope=scope,
            provider=self.name,
            raw=res,
        )

    def search(self, query: SearchQuery) -> list[SearchHit]:
        """Search memories in Mem0."""
        scope = query.scope or Scope()
        user_id = self._require_user_id(scope, "search")
        transport = self._get_transport()

        filters = query.filters if query.filters else self._build_scope_filters(scope)
        if not filters:
            filters = {"user_id": user_id}

        payload: Dict[str, Any] = {
            "query": query.query,
            "user_id": user_id,
            "limit": query.limit or 10,
        }
        if filters:
            payload["filters"] = filters

        res = transport.post("/v2/memories/search/", "search", json=payload)

        hits: list[SearchHit] = []
        items: list[Any] = []

        if isinstance(res, dict):
            for key in ("results", "data", "memories"):
                if isinstance(res.get(key), list):
                    items = res[key]
                    break
        elif isinstance(res, list):
            items = res

        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            mid = item.get("id") or item.get("memory_id") or "unknown"
            content = item.get("memory") or item.get("text") or item.get("content") or ""
            metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
            score = item.get("score")

            record = MemoryRecord(
                id=str(mid),
                content=str(content),
                metadata=dict(metadata),
                scope=scope,
                provider=self.name,
                raw=item,
            )
            hits.append(
                SearchHit(
                    record=record,
                    rank=idx + 1,
                    score=float(score) if isinstance(score, (int, float)) else None,
                )
            )

        return hits

    def list_memories(self, scope: Scope, limit: int = 100) -> list[MemoryRecord]:
        """List memories by scope (Mem0-specific)."""
        user_id = self._require_user_id(scope, "list")
        transport = self._get_transport()

        payload: Dict[str, Any] = {
            "user_id": user_id,
        }
        if scope.agent_id:
            payload["agent_id"] = scope.agent_id
        if scope.run_id:
            payload["run_id"] = scope.run_id

        res = transport.post("/v2/memories/", "list", json=payload)

        records: list[MemoryRecord] = []
        items: list[Any] = []

        if isinstance(res, dict):
            for key in ("results", "data", "memories"):
                if isinstance(res.get(key), list):
                    items = res[key]
                    break
        elif isinstance(res, list):
            items = res

        for item in items[:limit]:
            if not isinstance(item, dict):
                continue
            mid = item.get("id") or item.get("memory_id") or "unknown"
            content = item.get("memory") or item.get("text") or item.get("content") or ""
            metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}

            created_at = None
            if item.get("created_at"):
                try:
                    created_at = datetime.fromisoformat(
                        str(item["created_at"]).replace("Z", "+00:00")
                    )
                except Exception:
                    pass

            updated_at = None
            if item.get("updated_at"):
                try:
                    updated_at = datetime.fromisoformat(
                        str(item["updated_at"]).replace("Z", "+00:00")
                    )
                except Exception:
                    pass

            records.append(
                MemoryRecord(
                    id=str(mid),
                    content=str(content),
                    metadata=dict(metadata),
                    scope=scope,
                    provider=self.name,
                    created_at=created_at,
                    updated_at=updated_at,
                    raw=item,
                )
            )

        return records

    def get(self, memory_id: str, scope: Optional[Scope] = None) -> MemoryRecord:
        """Get a specific memory by ID."""
        transport = self._get_transport()

        res = transport.get(f"/v1/memories/{memory_id}", "get")

        content = ""
        metadata: Dict[str, Any] = {}
        created_at = None
        updated_at = None

        if isinstance(res, dict):
            content = str(res.get("memory") or res.get("text") or res.get("content") or "")
            if isinstance(res.get("metadata"), dict):
                metadata = dict(res["metadata"])
            if res.get("created_at"):
                try:
                    created_at = datetime.fromisoformat(
                        str(res["created_at"]).replace("Z", "+00:00")
                    )
                except Exception:
                    pass
            if res.get("updated_at"):
                try:
                    updated_at = datetime.fromisoformat(
                        str(res["updated_at"]).replace("Z", "+00:00")
                    )
                except Exception:
                    pass

        return MemoryRecord(
            id=str(memory_id),
            content=content,
            metadata=metadata,
            scope=scope or Scope(),
            provider=self.name,
            created_at=created_at,
            updated_at=updated_at,
            raw=res,
        )

    def delete(self, memory_id: str, scope: Optional[Scope] = None) -> None:
        """Delete a memory by ID."""
        transport = self._get_transport()
        transport.delete(f"/v1/memories/{memory_id}", "delete")

    def delete_by_scope(self, scope: Scope) -> int:
        """Delete all memories matching the scope."""
        user_id = self._require_user_id(scope, "delete_by_scope")
        transport = self._get_transport()

        # Mem0 supports bulk delete via DELETE /v1/memories/ with body filters
        payload: Dict[str, Any] = {
            "user_id": user_id,
        }
        if scope.agent_id:
            payload["agent_id"] = scope.agent_id
        if scope.run_id:
            payload["run_id"] = scope.run_id

        try:
            res = transport.request("DELETE", "/v1/memories/", "delete_by_scope", json=payload)

            if isinstance(res, dict):
                if isinstance(res.get("deleted"), int):
                    return int(res["deleted"])
                if res.get("message"):
                    return 0
            return 0
        except Exception:
            # Fallback: list + delete individually
            memories = self.list_memories(scope, limit=1000)
            deleted = 0
            for mem in memories:
                try:
                    self.delete(mem.id, scope)
                    deleted += 1
                except Exception:
                    pass
            return deleted
