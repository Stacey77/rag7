# Ragamuffin Python SDK

Official Python client library for the Ragamuffin AI platform.

## Installation

```bash
# From PyPI (when published)
pip install ragamuffin-sdk

# From source
pip install -e /path/to/sdk/python
```

## Quick Start

```python
from ragamuffin import RagamuffinClient

# Initialize client
client = RagamuffinClient("http://localhost:8000")

# Login
client.login("user@example.com", "password")

# Embed documents
result = client.rag.embed(["Document 1", "Document 2"])

# Search
results = client.rag.search("machine learning", top_k=5)

# RAG query
response = client.rag.query("What is machine learning?")
print(response)
```

## Features

### Authentication

```python
# Login
client.login("user@example.com", "password")

# Register new account
client.register("John Doe", "john@example.com", "securepassword")

# Get current user
user = client.auth.me()

# Logout
client.logout()
```

### RAG Operations

```python
# Embed text documents
client.rag.embed(
    texts=["Doc 1", "Doc 2"],
    collection="my_collection"
)

# Embed an image
client.rag.embed_image("path/to/image.jpg")

# Vector search
results = client.rag.search("query text", top_k=10)

# RAG query with context retrieval
response = client.rag.query("What is the meaning of life?")

# List collections
collections = client.rag.collections()
```

### Flow Management

```python
# List flows
flows = client.flows.list()

# Save a flow
client.flows.save("my_flow", {"nodes": [], "edges": []})

# Get a flow
flow = client.flows.get("my_flow")

# Run a flow
result = client.flows.run("my_flow", "Hello!")

# Delete a flow
client.flows.delete("my_flow")
```

### Voice (Retell.ai)

```python
# Check status
status = client.voice.status()

# List agents
agents = client.voice.agents()

# Create web call
call = client.voice.create_web_call("agent_123")

# Create phone call
call = client.voice.create_phone_call(
    agent_id="agent_123",
    to_phone="+1234567890"
)

# List calls
calls = client.voice.calls()

# End call
client.voice.end_call("call_123")
```

## Error Handling

```python
from ragamuffin import (
    RagamuffinClient,
    AuthenticationError,
    APIError,
    RateLimitError,
    NotFoundError,
)

client = RagamuffinClient("http://localhost:8000")

try:
    client.login("user@example.com", "wrong_password")
except AuthenticationError as e:
    print(f"Login failed: {e}")

try:
    result = client.rag.search("query")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except APIError as e:
    print(f"API error: {e}")
```

## Context Manager

```python
with RagamuffinClient("http://localhost:8000") as client:
    client.login("user@example.com", "password")
    results = client.rag.search("query")
# Client is automatically closed
```

## Direct Token Authentication

```python
# If you have tokens from another source
client = RagamuffinClient("http://localhost:8000")
client.set_tokens(
    access_token="your_access_token",
    refresh_token="your_refresh_token"
)
```

## API Reference

### RagamuffinClient

Main client class for interacting with the API.

**Parameters:**
- `base_url` (str): Base URL of the Ragamuffin API
- `timeout` (float): Request timeout in seconds (default: 30)
- `api_key` (str, optional): API key for authentication

**Methods:**
- `login(email, password)`: Login with credentials
- `register(name, email, password)`: Register new account
- `logout()`: Clear authentication tokens
- `set_tokens(access_token, refresh_token)`: Set tokens directly
- `health()`: Check API health

**Properties:**
- `auth`: AuthClient for authentication operations
- `rag`: RAGClient for RAG operations
- `flows`: FlowsClient for flow management
- `voice`: VoiceClient for voice/Retell operations

### RAGClient

**Methods:**
- `embed(texts, collection, metadata)`: Embed text documents
- `embed_image(image, collection, metadata)`: Embed images
- `search(query, top_k, collection, filter_expr)`: Vector search
- `query(query, top_k, collection, use_hybrid)`: RAG query
- `collections()`: List collections
- `create_collection(name, dimension, description)`: Create collection
- `delete_collection(name)`: Delete collection

### FlowsClient

**Methods:**
- `list()`: List all flows
- `get(name)`: Get flow by name
- `save(name, content)`: Save a flow
- `run(flow, user_input, tweaks)`: Execute a flow
- `delete(name)`: Delete a flow
- `export(name, path)`: Export flow to file
- `import_flow(path, name)`: Import flow from file

### VoiceClient

**Methods:**
- `status()`: Check Retell configuration
- `agents()`: List agents
- `get_agent(agent_id)`: Get agent details
- `create_web_call(agent_id, metadata, dynamic_variables)`: Start web call
- `create_phone_call(agent_id, to_phone, from_phone, metadata)`: Start phone call
- `calls(limit, offset)`: List call history
- `get_call(call_id)`: Get call details
- `end_call(call_id)`: End call
- `voices()`: List available voices

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=ragamuffin
```

## License

MIT License
