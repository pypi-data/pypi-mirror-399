"""
Supermemory provider adapter - HTTP-first implementation (no SDK dependency).

Endpoints:
- Add document: POST /v3/documents
- Search (low latency): POST /v4/search
- Search (documents): POST /v3/search
- Get document: GET /v3/documents/{id}
- Delete: DELETE /v3/documents/{id}
- List: GET /v3/documents
- Profile (optional): POST /v4/profile

Auth: Authorization: Bearer <SUPERMEMORY_API_KEY>
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from ...exceptions import ValidationError
from ...models import MemoryInput, MemoryRecord, ProviderCapabilities, Scope, SearchHit, SearchQuery
from ...provider import Provider
from .._shared import HTTPConfig, HTTPTransport, build_auth_header, join_messages


DEFAULT_BASE_URL = "https://api.supermemory.ai"


@dataclass
class SupermemoryProvider(Provider):
    """
    Supermemory provider using direct HTTP calls.

    No SDK installation required.
    """

    api_key: str
    base_url: Optional[str] = None
    timeout_s: float = 30.0
    extra: Dict[str, Any] | None = None

    name: str = "supermemory"
    _transport: HTTPTransport | None = field(default=None, init=False, repr=False)

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_delete_by_scope=True,
            supports_bulk=False,
        )

    def _get_transport(self) -> HTTPTransport:
        if self._transport is None:
            base = self.base_url or DEFAULT_BASE_URL
            config = HTTPConfig(
                base_url=base,
                auth_header=build_auth_header(self.api_key, "bearer"),
                timeout_s=self.timeout_s,
            )
            self._transport = HTTPTransport(config, provider=self.name)
        return self._transport

    def _scope_to_tags(self, scope: Scope) -> list[str]:
        """Convert Scope to container tags for Supermemory filtering."""
        tags: list[str] = []
        if scope.tags:
            tags.extend(scope.tags)
        if scope.user_id:
            tags.append(f"user:{scope.user_id}")
        if scope.agent_id:
            tags.append(f"agent:{scope.agent_id}")
        if scope.thread_id:
            tags.append(f"thread:{scope.thread_id}")
        if scope.run_id:
            tags.append(f"run:{scope.run_id}")
        return tags

    def add(self, input: MemoryInput, scope: Scope) -> MemoryRecord:
        """Add a document to Supermemory."""
        transport = self._get_transport()

        content = input.text
        if content is None:
            content = join_messages(input.messages or [])

        tags = self._scope_to_tags(scope)

        payload: Dict[str, Any] = {
            "content": content,
        }
        if tags:
            payload["containerTags"] = tags
        if input.metadata:
            payload["metadata"] = input.metadata
        if input.external_id:
            payload["customId"] = input.external_id

        res = transport.post("/v3/documents", "add", json=payload)

        memory_id = "unknown"
        if isinstance(res, dict):
            memory_id = str(
                res.get("id") or res.get("documentId") or res.get("memoryId") or "unknown"
            )

        return MemoryRecord(
            id=memory_id,
            content=content,
            metadata=input.metadata or {},
            scope=scope,
            provider=self.name,
            raw=res,
        )

    def search(self, query: SearchQuery) -> list[SearchHit]:
        """Search documents in Supermemory using low-latency v4 endpoint."""
        transport = self._get_transport()
        scope = query.scope or Scope()
        tags = self._scope_to_tags(scope)

        payload: Dict[str, Any] = {
            "q": query.query,
        }
        if query.limit:
            payload["limit"] = query.limit
        if tags:
            payload["containerTags"] = tags
        if query.filters:
            payload["filters"] = query.filters

        res = transport.post("/v4/search", "search", json=payload)

        items: List[Any] = []
        if isinstance(res, dict):
            # v4 response has "results" array
            if "response" in res and isinstance(res["response"], dict):
                items = res["response"].get("results", [])
            else:
                items = res.get("results") or res.get("data") or []
        elif isinstance(res, list):
            items = res

        hits: list[SearchHit] = []
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                continue

            # documentId is the primary ID in search results
            mid = item.get("documentId") or item.get("document_id") or item.get("id") or "unknown"

            # Content can be in chunks[0].content or top-level
            content = ""
            if "chunks" in item and isinstance(item["chunks"], list) and len(item["chunks"]) > 0:
                chunk = item["chunks"][0]
                if isinstance(chunk, dict):
                    content = chunk.get("content", "")
            if not content:
                content = item.get("content") or item.get("text") or ""

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

    def list_documents(self, scope: Scope, limit: int = 100) -> list[MemoryRecord]:
        """List documents by scope (Supermemory-specific)."""
        transport = self._get_transport()
        tags = self._scope_to_tags(scope)

        params: Dict[str, Any] = {}
        if tags:
            params["containerTags"] = ",".join(tags)
        if limit:
            params["limit"] = limit

        res = transport.get("/v3/documents", "list", params=params)

        items: List[Any] = []
        if isinstance(res, dict):
            items = (
                res.get("documents")
                or res.get("memories")
                or res.get("data")
                or res.get("results")
                or []
            )
        elif isinstance(res, list):
            items = res

        records: list[MemoryRecord] = []
        for item in items[:limit]:
            if not isinstance(item, dict):
                continue

            mid = item.get("id") or item.get("documentId") or "unknown"
            content = item.get("content") or item.get("text") or ""
            metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}

            created_at = None
            if item.get("createdAt"):
                try:
                    created_at = datetime.fromisoformat(
                        str(item["createdAt"]).replace("Z", "+00:00")
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
                    raw=item,
                )
            )

        return records

    def get(self, memory_id: str, scope: Optional[Scope] = None) -> MemoryRecord:
        """Get a specific document by ID."""
        transport = self._get_transport()

        res = transport.get(f"/v3/documents/{memory_id}", "get")

        content = ""
        metadata: Dict[str, Any] = {}
        created_at = None

        if isinstance(res, dict):
            content = str(res.get("content") or res.get("text") or "")
            if isinstance(res.get("metadata"), dict):
                metadata = dict(res["metadata"])
            if res.get("createdAt"):
                try:
                    created_at = datetime.fromisoformat(
                        str(res["createdAt"]).replace("Z", "+00:00")
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
            raw=res,
        )

    def delete(self, memory_id: str, scope: Optional[Scope] = None) -> None:
        """Delete a document by ID."""
        transport = self._get_transport()
        transport.delete(f"/v3/documents/{memory_id}", "delete")

    def delete_by_scope(self, scope: Scope) -> int:
        """Delete all documents matching the scope."""
        tags = self._scope_to_tags(scope)
        if not tags:
            raise ValidationError(
                "delete_by_scope for Supermemory requires at least one tag or user_id",
                provider=self.name,
                operation="delete_by_scope",
            )

        # Supermemory doesn't have a bulk delete by tag, so we list + delete individually
        documents = self.list_documents(scope, limit=1000)

        deleted = 0
        for doc in documents:
            try:
                self.delete(doc.id, scope)
                deleted += 1
            except Exception:
                pass  # Continue deleting others

        return deleted

    def get_profile(self, scope: Scope) -> Dict[str, Any]:
        """
        Get user profile from Supermemory (optional capability).

        Returns structured facts about the user.
        """
        transport = self._get_transport()
        tags = self._scope_to_tags(scope)

        payload: Dict[str, Any] = {}
        if tags:
            payload["containerTags"] = tags

        res = transport.post("/v4/profile", "profile", json=payload)

        return res if isinstance(res, dict) else {"raw": res}
