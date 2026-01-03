"""
Letta provider adapter - HTTP-first implementation (no SDK dependency).

Base URL: https://api.letta.com
Auth: Authorization: Bearer <LETTA_API_KEY>

Endpoints (archives/passages - preferred):
- Create archive: POST /v1/archives/
- List archives: GET /v1/archives/
- Create passage: POST /v1/archives/{archive_id}/passages
- List passages: GET /v1/archives/{archive_id}/passages
- Delete passage: DELETE /v1/archives/{archive_id}/passages/{passage_id}
- Search passages: POST /v1/passages/search

Legacy (agent archival memory - still usable):
- List agent passages: GET /v1/agents/{agent_id}/archival-memory
- Create agent passage: POST /v1/agents/{agent_id}/archival-memory
- Delete agent passage: DELETE /v1/agents/{agent_id}/archival-memory/{memory_id}
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ...exceptions import NotFoundError, ValidationError
from ...models import MemoryInput, MemoryRecord, ProviderCapabilities, Scope, SearchHit, SearchQuery
from ...provider import Provider
from .._shared import HTTPConfig, HTTPTransport, build_auth_header, join_messages


DEFAULT_BASE_URL = "https://api.letta.com"


@dataclass
class LettaProvider(Provider):
    """
    Letta provider using direct HTTP calls.

    No SDK installation required.

    Supports two modes:
    1. Archives mode (default): Uses standalone archives/passages API
       - Requires archive_id (from extra config or auto-created per user)
    2. Agent mode: Uses agent archival memory API
       - Requires agent_id in scope
    """

    api_key: str
    base_url: Optional[str] = None
    timeout_s: float = 30.0
    extra: Dict[str, Any] | None = None
    use_agent_mode: bool = False  # If True, use agent archival memory API

    name: str = "letta"
    _transport: HTTPTransport | None = field(default=None, init=False, repr=False)
    _archive_cache: Dict[str, str] = field(default_factory=dict, init=False, repr=False)

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_agents=True,
            supports_streaming=True,
            supports_delete_by_scope=True,
        )

    def _get_transport(self) -> HTTPTransport:
        if self._transport is None:
            base = self.base_url or DEFAULT_BASE_URL
            headers: Dict[str, str] = {}
            if self.extra:
                if self.extra.get("project_id"):
                    headers["X-Project-Id"] = str(self.extra["project_id"])
                if self.extra.get("project"):
                    headers["X-Project"] = str(self.extra["project"])

            config = HTTPConfig(
                base_url=base,
                auth_header=build_auth_header(self.api_key, "bearer"),
                timeout_s=self.timeout_s,
                headers=headers,
            )
            self._transport = HTTPTransport(config, provider=self.name)
        return self._transport

    def _require_agent_id(self, scope: Scope, operation: str) -> str:
        if not scope.agent_id:
            raise ValidationError(
                "Letta requires scope.agent_id", provider=self.name, operation=operation
            )
        return scope.agent_id

    # ─────────────────────────────────────────────────────────────────
    # Archive management (standalone archives API)
    # ─────────────────────────────────────────────────────────────────

    def create_archive(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Create an archive."""
        transport = self._get_transport()
        payload: Dict[str, Any] = {
            "name": name,
        }
        if description:
            payload["description"] = description

        return transport.post("/v1/archives/", "create_archive", json=payload)

    def list_archives(self) -> List[Dict[str, Any]]:
        """List all archives."""
        transport = self._get_transport()
        res = transport.get("/v1/archives/", "list_archives")
        if isinstance(res, list):
            return res
        if isinstance(res, dict) and "archives" in res:
            return res["archives"]
        return []

    def get_or_create_archive(self, user_id: str) -> str:
        """Get or create an archive for a user. Returns archive_id."""
        # Check cache first
        if user_id in self._archive_cache:
            return self._archive_cache[user_id]

        # Check if archive exists
        archive_name = f"unicontext-{user_id}"
        archives = self.list_archives()

        for arch in archives:
            if isinstance(arch, dict) and arch.get("name") == archive_name:
                archive_id = str(arch.get("id"))
                self._archive_cache[user_id] = archive_id
                return archive_id

        # Create new archive
        res = self.create_archive(archive_name, f"UniContext archive for user {user_id}")
        archive_id = str(res.get("id"))
        self._archive_cache[user_id] = archive_id
        return archive_id

    # ─────────────────────────────────────────────────────────────────
    # Passages (archive-based)
    # ─────────────────────────────────────────────────────────────────

    def create_passage(
        self, archive_id: str, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a passage in an archive."""
        transport = self._get_transport()
        payload: Dict[str, Any] = {
            "text": text,
        }
        if metadata:
            payload["metadata"] = metadata

        res = transport.post(f"/v1/archives/{archive_id}/passages", "create_passage", json=payload)

        # Response may be a list with one item
        if isinstance(res, list) and len(res) > 0:
            return res[0]
        return res

    def list_passages(self, archive_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """List passages in an archive."""
        transport = self._get_transport()
        params = {"limit": limit}
        res = transport.get(f"/v1/archives/{archive_id}/passages", "list_passages", params=params)

        if isinstance(res, list):
            return res
        if isinstance(res, dict) and "passages" in res:
            return res["passages"]
        return []

    def delete_passage(self, archive_id: str, passage_id: str) -> None:
        """Delete a passage from an archive."""
        transport = self._get_transport()
        transport.delete(f"/v1/archives/{archive_id}/passages/{passage_id}", "delete_passage")

    def search_passages(
        self,
        query: str,
        archive_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search passages across archives or by agent."""
        transport = self._get_transport()
        payload: Dict[str, Any] = {
            "query": query,
            "limit": limit,
        }
        if archive_id:
            payload["archive_id"] = archive_id
        if agent_id:
            payload["agent_id"] = agent_id

        res = transport.post("/v1/passages/search", "search_passages", json=payload)

        if isinstance(res, list):
            return res
        if isinstance(res, dict):
            return res.get("results") or res.get("passages") or []
        return []

    # ─────────────────────────────────────────────────────────────────
    # Agent archival memory (legacy mode)
    # ─────────────────────────────────────────────────────────────────

    def create_agent_passage(self, agent_id: str, text: str) -> Dict[str, Any]:
        """Create a passage in agent's archival memory (legacy API)."""
        transport = self._get_transport()
        payload: Dict[str, Any] = {
            "text": text,
        }

        res = transport.post(
            f"/v1/agents/{agent_id}/archival-memory", "create_agent_passage", json=payload
        )

        if isinstance(res, list) and len(res) > 0:
            return res[0]
        return res

    def list_agent_passages(self, agent_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """List passages in agent's archival memory (legacy API)."""
        transport = self._get_transport()
        params = {"limit": limit}
        res = transport.get(
            f"/v1/agents/{agent_id}/archival-memory", "list_agent_passages", params=params
        )

        if isinstance(res, list):
            return res
        if isinstance(res, dict):
            return res.get("passages") or res.get("archival_memory") or []
        return []

    def delete_agent_passage(self, agent_id: str, memory_id: str) -> None:
        """Delete a passage from agent's archival memory (legacy API)."""
        transport = self._get_transport()
        transport.delete(
            f"/v1/agents/{agent_id}/archival-memory/{memory_id}", "delete_agent_passage"
        )

    # ─────────────────────────────────────────────────────────────────
    # Provider interface implementation
    # ─────────────────────────────────────────────────────────────────

    def add(self, input: MemoryInput, scope: Scope) -> MemoryRecord:
        """Add memory using Letta archives/passages or agent archival memory."""
        content = input.text
        if content is None:
            content = join_messages(input.messages or [])

        # Agent mode: use agent archival memory API
        if self.use_agent_mode or (scope.agent_id and not scope.user_id):
            agent_id = self._require_agent_id(scope, "add")
            res = self.create_agent_passage(agent_id, content)

            passage_id = str(res.get("id")) if isinstance(res, dict) else "unknown"
            return MemoryRecord(
                id=passage_id,
                content=content,
                metadata=input.metadata or {},
                scope=scope,
                provider=self.name,
                raw=res,
            )

        # Archive mode: use standalone archives/passages API
        if not scope.user_id:
            raise ValidationError(
                "Letta requires scope.user_id (for archive mode) or scope.agent_id (for agent mode)",
                provider=self.name,
                operation="add",
            )

        # Get or create archive for user
        archive_id = self.extra.get("archive_id") if self.extra else None
        if not archive_id:
            archive_id = self.get_or_create_archive(scope.user_id)

        res = self.create_passage(archive_id, content, input.metadata)

        passage_id = str(res.get("id")) if isinstance(res, dict) else "unknown"
        return MemoryRecord(
            id=passage_id,
            content=content,
            metadata=input.metadata or {},
            scope=scope,
            provider=self.name,
            raw=res,
        )

    def search(self, query: SearchQuery) -> list[SearchHit]:
        """Search passages using Letta's search API."""
        scope = query.scope or Scope()

        # Determine search context
        archive_id = self.extra.get("archive_id") if self.extra else None
        agent_id = scope.agent_id if (self.use_agent_mode or not scope.user_id) else None

        if not archive_id and scope.user_id and not agent_id:
            # Get archive for user
            archive_id = self.get_or_create_archive(scope.user_id)

        items = self.search_passages(
            query.query,
            archive_id=archive_id,
            agent_id=agent_id,
            limit=query.limit or 10,
        )

        hits: list[SearchHit] = []
        for rank, item in enumerate(items, start=1):
            if not isinstance(item, dict):
                continue

            # Handle search response structure (may have .passage attribute)
            passage = item.get("passage", item)
            score = float(item.get("score", 0.0)) if "score" in item else None

            passage_id = str(passage.get("id")) if isinstance(passage, dict) else "unknown"
            text = str(passage.get("text", "")) if isinstance(passage, dict) else ""
            metadata = passage.get("metadata", {}) if isinstance(passage, dict) else {}

            record = MemoryRecord(
                id=passage_id,
                content=text,
                metadata=metadata if isinstance(metadata, dict) else {},
                scope=scope,
                provider=self.name,
                raw=item,
            )

            hits.append(SearchHit(record=record, rank=rank, score=score))

        return hits

    def get(self, memory_id: str, scope: Optional[Scope] = None) -> MemoryRecord:
        """Get memory by ID using list and filter."""
        if not scope:
            raise ValidationError(
                "Letta requires scope with user_id or agent_id for get()",
                provider=self.name,
                operation="get",
            )

        # Determine which API to use
        if self.use_agent_mode or (scope.agent_id and not scope.user_id):
            agent_id = self._require_agent_id(scope, "get")
            passages = self.list_agent_passages(agent_id)
        else:
            if not scope.user_id:
                raise ValidationError(
                    "Letta requires scope.user_id for archive mode get()",
                    provider=self.name,
                    operation="get",
                )
            archive_id = self.extra.get("archive_id") if self.extra else None
            if not archive_id:
                archive_id = self.get_or_create_archive(scope.user_id)
            passages = self.list_passages(archive_id)

        # Find matching passage
        for passage in passages:
            if isinstance(passage, dict) and str(passage.get("id")) == memory_id:
                return MemoryRecord(
                    id=str(passage["id"]),
                    content=str(passage.get("text", "")),
                    metadata=passage.get("metadata", {})
                    if isinstance(passage.get("metadata"), dict)
                    else {},
                    scope=scope,
                    provider=self.name,
                    raw=passage,
                )

        raise NotFoundError(f"Memory {memory_id} not found", provider=self.name, operation="get")

    def delete(self, memory_id: str, scope: Optional[Scope] = None) -> None:
        """Delete memory by ID."""
        if not scope:
            raise ValidationError(
                "Letta requires scope with user_id or agent_id for delete()",
                provider=self.name,
                operation="delete",
            )

        # Determine which API to use
        if self.use_agent_mode or (scope.agent_id and not scope.user_id):
            agent_id = self._require_agent_id(scope, "delete")
            self.delete_agent_passage(agent_id, memory_id)
        else:
            if not scope.user_id:
                raise ValidationError(
                    "Letta requires scope.user_id for archive mode delete()",
                    provider=self.name,
                    operation="delete",
                )
            archive_id = self.extra.get("archive_id") if self.extra else None
            if not archive_id:
                archive_id = self.get_or_create_archive(scope.user_id)
            self.delete_passage(archive_id, memory_id)

    def delete_by_scope(self, scope: Scope) -> int:
        """Delete all memories for a scope."""
        # Determine which API to use
        if self.use_agent_mode or (scope.agent_id and not scope.user_id):
            agent_id = self._require_agent_id(scope, "delete_by_scope")
            passages = self.list_agent_passages(agent_id)

            deleted = 0
            for passage in passages:
                if isinstance(passage, dict) and passage.get("id"):
                    try:
                        self.delete_agent_passage(agent_id, str(passage["id"]))
                        deleted += 1
                    except Exception:
                        pass
            return deleted
        else:
            if not scope.user_id:
                raise ValidationError(
                    "Letta requires scope.user_id for archive mode delete_by_scope()",
                    provider=self.name,
                    operation="delete_by_scope",
                )
            archive_id = self.extra.get("archive_id") if self.extra else None
            if not archive_id:
                archive_id = self.get_or_create_archive(scope.user_id)

            passages = self.list_passages(archive_id)

            deleted = 0
            for passage in passages:
                if isinstance(passage, dict) and passage.get("id"):
                    try:
                        self.delete_passage(archive_id, str(passage["id"]))
                        deleted += 1
                    except Exception:
                        pass
            return deleted
