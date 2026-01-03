# State Management with NATS JetStream KV Store

`kryten-py` provides built-in helpers for using NATS JetStream KeyValue (KV) stores. This allows services to persist state (user stats, configuration, moderation logs) without external databases.

## Core Concepts

NATS KV stores are lightweight, persistent key-value buckets.

*   **Buckets:** Logical containers for keys (e.g., `kryten_user_stats`).
*   **Keys:** String identifiers (e.g., `user:bob`).
*   **Values:** Byte arrays (automatically handled as JSON/Strings by helpers).

## 1. Accessing Stores: `get` vs `create`

A critical distinction exists between **binding** to an existing store and **provisioning** a new one.

### `get_kv_store` (Bind)
**Use when:** Your service *consumes* or *writes* to a bucket managed by another service (usually `kryten-robot`).
**Behavior:** Connects to an existing bucket. Fails if the bucket does not exist.

```python
from kryten.kv_store import get_kv_store

# Access the shared user stats bucket (must already exist)
kv = await get_kv_store(client._nats, "kryten_user_stats", logger=client.logger)
```

### `get_or_create_kv_store` (Provision)
**Use when:** Your service *owns* the data and is responsible for its lifecycle.
**Behavior:** Connects to the bucket if it exists; otherwise, creates it with specific configuration (history size, storage type, etc.).

```python
from kryten.kv_store import get_or_create_kv_store

# Access OR create a bucket for this service's private state
kv = await get_or_create_kv_store(
    client._nats, 
    "kryten_llm_state", 
    description="LLM Service Context Storage",
    max_value_size=1024 * 1024,  # 1MB
    logger=client.logger
)
```

## 2. CRUD Operations

The library provides async helper functions that handle encoding/decoding and error logging.

### Writing Data (`kv_put`)
Supports raw bytes, strings, or JSON-serializable dictionaries.

```python
from kryten.kv_store import kv_put

# Store a string
await kv_put(kv, "last_seen", "2025-01-01T12:00:00Z")

# Store a complex object (auto-JSON serialization)
user_data = {"rank": 2, "points": 500}
await kv_put(kv, "user:bob", user_data, as_json=True)
```

### Reading Data (`kv_get`)
Retrieves data with optional JSON parsing and default values.

```python
from kryten.kv_store import kv_get

# Get string (returns None if missing)
timestamp = await kv_get(kv, "last_seen")

# Get JSON with default fallback
data = await kv_get(kv, "user:bob", default={"rank": 0}, parse_json=True)
print(f"User Rank: {data['rank']}")
```

### Deleting Data (`kv_delete`)
Removes a key. Note that NATS KV supports history, so previous values might still exist in the stream depending on bucket config.

```python
from kryten.kv_store import kv_delete

await kv_delete(kv, "user:bob")
```

### Listing Keys (`kv_keys` / `kv_get_all`)

```python
from kryten.kv_store import kv_keys, kv_get_all

# Get list of all keys
keys = await kv_keys(kv)

# Get complete dictionary of all data
all_data = await kv_get_all(kv, parse_json=True)
```

## 3. Best Practices

1.  **Bucket Ownership:** Only one service should be responsible for *creating* (`get_or_create`) a specific bucket. Other services should use `get_kv_store`.
2.  **Naming Conventions:** Prefix buckets with `kryten_` and the service/domain name (e.g., `kryten_moderator_logs`).
3.  **JSON Serialization:** Always use `as_json=True` / `parse_json=True` for structured data to ensure consistent encoding.
4.  **Error Handling:** The helpers log errors automatically, but they generally return `None` or `False` on failure rather than raising exceptions (to prevent crashing the event loop). Check return values!

## 4. Example: User Counter Service

```python
async def update_count(client, username):
    # 1. Bind to store
    kv = await get_or_create_kv_store(client._nats, "kryten_message_counts")
    
    # 2. Get current value
    key = f"user:{username}"
    count = await kv_get(kv, key, default=0, parse_json=True)
    
    # 3. Increment
    count += 1
    
    # 4. Save
    await kv_put(kv, key, count, as_json=True)
```
