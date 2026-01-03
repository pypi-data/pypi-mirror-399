# UniContext

Universal Python SDK for agent memory and context with a unified API across multiple providers.

UniContext is HTTP-first: built-in providers call provider REST APIs via `httpx`. Switch providers by changing the provider name and API key.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- Unified, provider-agnostic client API
- Typed models and input validation
- Consistent error types across providers
- Shared HTTP transport (connection pooling)

## Installation

From PyPI:

```bash
pip install unicontext
```

From source (development):

```bash
pip install -e .
```

Optional development tools:

```bash
pip install -e ".[dev]"
```

## Quick start

This example uses Letta (archives mode) because it has synchronous IDs you can `get()` and `delete()` immediately.

```python
from unicontext import MemoryInput, Scope, SearchQuery, create_client

client = create_client(provider="letta", api_key="YOUR_LETTA_API_KEY")
scope = Scope(user_id="user_123")

created = client.add(MemoryInput(text="User prefers Python for backend"), scope)

hits = client.search(SearchQuery(query="backend", scope=scope, limit=5))
for hit in hits:
    print(hit.record.content)

fetched = client.get(memory_id=created.id, scope=scope)
print(fetched.content)

client.delete(memory_id=created.id, scope=scope)
```

## Switching providers

```python
from unicontext import create_client

mem0 = create_client(provider="mem0", api_key="YOUR_MEM0_API_KEY")
supermemory = create_client(provider="supermemory", api_key="YOUR_SUPERMEMORY_API_KEY")
zep = create_client(provider="zep", api_key="YOUR_ZEP_API_KEY")
letta = create_client(provider="letta", api_key="YOUR_LETTA_API_KEY")
```

## Core concepts

### Scope

`Scope` selects where the memory lives (user, agent, thread, tags).

```python
from unicontext import Scope

Scope(user_id="user_123")
Scope(user_id="user_123", thread_id="thread_456")
Scope(user_id="user_123", tags=["preferences", "onboarding"])
```

### Inputs

`MemoryInput` must provide exactly one of `text` or `messages`.

```python
from unicontext import MemoryInput

MemoryInput(text="User prefers dark mode")
MemoryInput(messages=[{"role": "user", "content": "Hi"}])
```

## Provider notes

UniContext normalizes the public API, but providers have different semantics.

### Mem0

- `add()` is asynchronous; the returned ID may be an event ID.
- Use `search()` after processing completes to retrieve the finalized memory ID.

```python
import time

from unicontext import MemoryInput, Scope, SearchQuery, create_client

client = create_client(provider="mem0", api_key="YOUR_MEM0_API_KEY")
scope = Scope(user_id="user_123")

client.add(MemoryInput(text="User likes espresso"), scope)
time.sleep(20)

hits = client.search(SearchQuery(query="espresso", scope=scope, limit=5))
if hits:
    memory_id = hits[0].record.id
    client.delete(memory_id=memory_id, scope=scope)
```

### Supermemory

- Scope is primarily tag-driven.
- `delete_by_scope()` requires at least one tag to reduce accidental deletes.

### Zep

- Dual routing: if `scope.thread_id` is set, `add()` writes to a thread; otherwise it writes to the knowledge graph.
- `search()` targets the knowledge graph.
- `get()` and `delete()` are not supported for graph records.

### Letta

- Default mode uses archives and passages.
- If you do not provide an archive ID, UniContext auto-creates and caches one per `scope.user_id`.

## Error handling

```python
from unicontext import Scope, SearchQuery, create_client
from unicontext.exceptions import AuthError, ProviderError, ValidationError

client = create_client(provider="letta", api_key="YOUR_LETTA_API_KEY")
scope = Scope(user_id="user_123")

try:
    client.search(SearchQuery(query="hello", scope=scope, limit=5))
except ValidationError as e:
    print(e.message)
except AuthError as e:
    print(e.message)
except ProviderError as e:
    print(e.message)
```

## Development

Run unit tests:

```bash
python -m pytest -v
```

Run the pre-release checks:

```bash
python scripts/pre_release.py
```
