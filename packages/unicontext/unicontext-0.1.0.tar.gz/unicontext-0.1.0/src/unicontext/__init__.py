"""UniContext: Universal Python SDK for AI memory/context providers.

HTTP-first architecture with support for Mem0, Supermemory, Zep, and Letta.
"""

from ._version import __version__
from .client import AsyncContextClient, ContextClient
from .factory import create_client
from .models import MemoryInput, MemoryRecord, Scope, SearchHit, SearchQuery

__all__ = [
    "__version__",
    "AsyncContextClient",
    "ContextClient",
    "MemoryInput",
    "MemoryRecord",
    "Scope",
    "SearchHit",
    "SearchQuery",
    "create_client",
]
