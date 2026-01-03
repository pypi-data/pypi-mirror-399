"""
Zep provider adapter - HTTP-first implementation (no SDK dependency).

Base URL: https://api.getzep.com/api/v2
Auth: Authorization: Api-Key <ZEP_API_KEY>

Endpoints:
- Create user: POST /users
- Get user: GET /users/{userId}
- Create thread: POST /threads
- Get thread: GET /threads/{threadId}
- Add messages: POST /threads/{threadId}/messages
- Get context block: GET /threads/{threadId}/context
- Add graph data: POST /graph
- Search graph: POST /graph/search
- Delete thread: DELETE /threads/{threadId}
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ...exceptions import NotSupportedError, ValidationError
from ...models import MemoryInput, MemoryRecord, ProviderCapabilities, Scope, SearchHit, SearchQuery
from ...provider import Provider
from .._shared import HTTPConfig, HTTPTransport, build_auth_header, join_messages


DEFAULT_BASE_URL = "https://api.getzep.com/api/v2"


@dataclass
class ZepProvider(Provider):
    """
    Zep provider using direct HTTP calls.

    No SDK installation required.

    Zep is fundamentally thread/context-based rather than just "memories".
    This adapter provides:
    - Thread-based message addition (when thread_id in scope)
    - Graph-based data ingestion (when no thread_id)
    - Context block retrieval
    - Graph search
    """

    api_key: str
    base_url: Optional[str] = None
    timeout_s: float = 30.0
    extra: Dict[str, Any] | None = None
    auto_create_user: bool = True  # Auto-create user if not exists
    auto_create_thread: bool = True  # Auto-create thread if not exists

    name: str = "zep"
    _transport: HTTPTransport | None = field(default=None, init=False, repr=False)

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_threads=True,
            supports_graph=True,
            supports_delete_by_scope=True,
        )

    def _get_transport(self) -> HTTPTransport:
        if self._transport is None:
            base = self.base_url or DEFAULT_BASE_URL
            config = HTTPConfig(
                base_url=base,
                auth_header=build_auth_header(self.api_key, "api-key"),
                timeout_s=self.timeout_s,
            )
            self._transport = HTTPTransport(config, provider=self.name)
        return self._transport

    def _require_user_id(self, scope: Scope, operation: str) -> str:
        if not scope.user_id:
            raise ValidationError(
                "Zep requires scope.user_id", provider=self.name, operation=operation
            )
        return scope.user_id

    # ─────────────────────────────────────────────────────────────────
    # User management
    # ─────────────────────────────────────────────────────────────────

    def create_user(
        self, user_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a user in Zep."""
        transport = self._get_transport()
        payload: Dict[str, Any] = {
            "user_id": user_id,
        }
        if metadata:
            payload["metadata"] = metadata

        return transport.post("/users", "create_user", json=payload)

    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user info."""
        transport = self._get_transport()
        return transport.get(f"/users/{user_id}", "get_user")

    def _ensure_user(self, user_id: str) -> None:
        """Ensure user exists, create if auto_create_user is True."""
        transport = self._get_transport()
        try:
            transport.get(f"/users/{user_id}", "ensure_user")
        except Exception:
            if self.auto_create_user:
                self.create_user(user_id)
            else:
                raise

    # ─────────────────────────────────────────────────────────────────
    # Thread management
    # ─────────────────────────────────────────────────────────────────

    def create_thread(
        self,
        user_id: str,
        thread_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a thread in Zep."""
        transport = self._get_transport()
        self._ensure_user(user_id)

        if not thread_id:
            raise ValidationError(
                "Zep create_thread requires thread_id",
                provider=self.name,
                operation="create_thread",
            )

        payload: Dict[str, Any] = {
            "user_id": user_id,
            "thread_id": thread_id,
        }
        if metadata:
            payload["metadata"] = metadata

        return transport.post("/threads", "create_thread", json=payload)

    def get_thread(self, thread_id: str) -> Dict[str, Any]:
        """Get thread info."""
        transport = self._get_transport()
        return transport.get(f"/threads/{thread_id}", "get_thread")

    def _ensure_thread(self, user_id: str, thread_id: str) -> None:
        """Ensure thread exists, create if auto_create_thread is True."""
        transport = self._get_transport()
        try:
            transport.get(f"/threads/{thread_id}", "ensure_thread")
        except Exception:
            if self.auto_create_thread:
                self.create_thread(user_id, thread_id)
            else:
                raise

    def delete_thread(self, thread_id: str) -> None:
        """Delete a thread."""
        transport = self._get_transport()
        transport.delete(f"/threads/{thread_id}", "delete_thread")

    # ─────────────────────────────────────────────────────────────────
    # Messages (thread-based)
    # ─────────────────────────────────────────────────────────────────

    def add_messages(
        self,
        thread_id: str,
        messages: List[Dict[str, str]],
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add messages to a thread."""
        transport = self._get_transport()

        # Ensure thread exists
        if user_id and self.auto_create_thread:
            self._ensure_thread(user_id, thread_id)

        # Format messages for Zep API
        zep_messages = []
        for msg in messages:
            zep_msg: Dict[str, Any] = {
                "role": msg.get("role", "user"),
                "content": msg.get("content", ""),
            }
            zep_messages.append(zep_msg)

        payload: Dict[str, Any] = {
            "messages": zep_messages,
        }

        return transport.post(f"/threads/{thread_id}/messages", "add_messages", json=payload)

    def get_context(
        self,
        thread_id: str,
        *,
        min_rating: Optional[float] = None,
        template_id: Optional[str] = None,
        mode: str = "summary",
        last_n: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get context block for a thread.

        Returns structured context including relevant memories and facts.
        """
        transport = self._get_transport()
        params: Dict[str, Any] = {}
        if min_rating is not None:
            params["minRating"] = min_rating
        if template_id is not None:
            params["template_id"] = template_id
        if mode:
            params["mode"] = mode
        # last_n is not supported by Zep v2 context endpoint; accept it for backward compatibility.

        return transport.get(f"/threads/{thread_id}/context", "get_context", params=params)

    # ─────────────────────────────────────────────────────────────────
    # Graph operations
    # ─────────────────────────────────────────────────────────────────

    def add_to_graph(
        self,
        data: str,
        user_id: str,
        data_type: str = "text",
    ) -> Dict[str, Any]:
        """Add data to the user's graph."""
        transport = self._get_transport()
        self._ensure_user(user_id)

        payload: Dict[str, Any] = {
            "type": data_type,
            "data": data,
            "user_id": user_id,
        }

        return transport.post("/graph", "add_to_graph", json=payload)

    def search_graph(
        self,
        query: str,
        user_id: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search the user's graph."""
        transport = self._get_transport()

        payload: Dict[str, Any] = {
            "query": query,
            "user_id": user_id,
            "limit": limit,
        }

        res = transport.post("/graph/search", "search_graph", json=payload)

        # Extract results
        if isinstance(res, dict):
            for key in ("results", "edges", "nodes", "episodes"):
                if isinstance(res.get(key), list):
                    return res[key]
            return []
        elif isinstance(res, list):
            return res
        return []

    # ─────────────────────────────────────────────────────────────────
    # Provider interface implementation
    # ─────────────────────────────────────────────────────────────────

    def add(self, input: MemoryInput, scope: Scope) -> MemoryRecord:
        """
        Add memory to Zep.

        Routing rules:
        - If thread_id exists: add as thread messages
        - Else: ingest into graph as text
        """
        user_id = self._require_user_id(scope, "add")

        # Thread-based message addition
        if scope.thread_id:
            messages = input.messages
            if messages is None:
                messages = [{"role": "user", "content": input.text or ""}]

            res = self.add_messages(scope.thread_id, messages, user_id=user_id)
            content = join_messages(messages)

            return MemoryRecord(
                id=f"thread:{scope.thread_id}",
                content=content,
                metadata=input.metadata or {},
                scope=scope,
                provider=self.name,
                raw=res,
            )

        # Graph-based ingestion
        text = input.text
        if text is None:
            text = join_messages(input.messages or [])

        res = self.add_to_graph(text, user_id)

        return MemoryRecord(
            id="graph:accepted",
            content=text,
            metadata=input.metadata or {},
            scope=scope,
            provider=self.name,
            raw=res,
        )

    def search(self, query: SearchQuery) -> list[SearchHit]:
        """Search Zep graph."""
        scope = query.scope or Scope()
        user_id = self._require_user_id(scope, "search")

        items = self.search_graph(query.query, user_id, limit=query.limit or 10)

        hits: list[SearchHit] = []
        for idx, item in enumerate(items):
            content = ""
            mid = f"hit:{idx}"
            metadata: Dict[str, Any] = {}

            if isinstance(item, dict):
                content = str(item.get("content") or item.get("text") or item.get("fact") or "")
                mid = str(item.get("id") or item.get("uuid") or f"hit:{idx}")
                metadata = {k: v for k, v in item.items() if k not in ("content", "text", "fact")}
            else:
                content = str(item)

            record = MemoryRecord(
                id=mid,
                content=content,
                metadata=metadata,
                scope=scope,
                provider=self.name,
                raw=item,
            )
            hits.append(SearchHit(record=record, rank=idx + 1, score=None))

        return hits

    def get(self, memory_id: str, scope: Optional[Scope] = None) -> MemoryRecord:
        """
        Get memory by ID.

        Zep doesn't expose a universal get-by-id for graph items.
        For thread context, use get_context() instead.
        """
        raise NotSupportedError(
            "Zep does not expose a universal get-by-id for graph/memory items. "
            "Use get_context(thread_id) for thread-based context, or search() for graph queries.",
            provider=self.name,
            operation="get",
        )

    def delete(self, memory_id: str, scope: Optional[Scope] = None) -> None:
        """
        Delete memory by ID.

        Zep delete-by-id is not supported in the universal API.
        Use delete_thread() for thread management.
        """
        raise NotSupportedError(
            "Zep delete-by-id is not supported. Use delete_thread(thread_id) or delete_by_scope().",
            provider=self.name,
            operation="delete",
        )

    def delete_by_scope(self, scope: Scope) -> int:
        """
        Delete by scope.

        Only supported when scope.thread_id is provided (deletes the thread).
        """
        if not scope.thread_id:
            raise NotSupportedError(
                "Zep delete_by_scope requires scope.thread_id (deletes the thread).",
                provider=self.name,
                operation="delete_by_scope",
            )

        self.delete_thread(scope.thread_id)
        return 1
