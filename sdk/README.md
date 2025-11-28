# Ragamuffin SDK

Official client libraries for the Ragamuffin AI platform.

## Available SDKs

| Language | Package | Status |
|----------|---------|--------|
| Python | `ragamuffin-sdk` | ✅ Ready |
| JavaScript/TypeScript | `@ragamuffin/sdk` | ✅ Ready |

## Installation

### Python

```bash
# From PyPI (when published)
pip install ragamuffin-sdk

# From source
pip install -e sdk/python/
```

### JavaScript/TypeScript

```bash
# From npm (when published)
npm install @ragamuffin/sdk

# From source
npm install sdk/javascript/
```

## Quick Examples

### Python

```python
from ragamuffin import RagamuffinClient

client = RagamuffinClient("http://localhost:8000")
client.login("user@example.com", "password")

# Embed and search
client.rag.embed(["Document 1", "Document 2"])
results = client.rag.search("query", top_k=5)

# RAG query
response = client.rag.query("What is machine learning?")
```

### JavaScript/TypeScript

```typescript
import { RagamuffinClient } from '@ragamuffin/sdk';

const client = new RagamuffinClient('http://localhost:8000');
await client.login('user@example.com', 'password');

// Embed and search
await client.rag.embed(['Document 1', 'Document 2']);
const results = await client.rag.search('query', { topK: 5 });

// RAG query
const response = await client.rag.query('What is machine learning?');
```

## Features

Both SDKs provide:

- **Authentication**: Login, register, token management
- **RAG Operations**: Embed text/images, search, query
- **Flow Management**: Save, list, run LangFlow flows
- **Voice (Retell.ai)**: Create web/phone calls, manage agents
- **Error Handling**: Custom exceptions with details
- **Type Safety**: Full type definitions (Python hints, TypeScript)

## Documentation

- [Python SDK README](./python/README.md)
- [JavaScript SDK README](./javascript/README.md)

## API Coverage

| Feature | Python | JavaScript |
|---------|--------|------------|
| Login/Register | ✅ | ✅ |
| Token Refresh | ✅ | ✅ |
| Embed Text | ✅ | ✅ |
| Embed Image | ✅ | ✅ |
| Vector Search | ✅ | ✅ |
| RAG Query | ✅ | ✅ |
| Collections | ✅ | ✅ |
| List Flows | ✅ | ✅ |
| Save Flow | ✅ | ✅ |
| Run Flow | ✅ | ✅ |
| Voice Status | ✅ | ✅ |
| Web Calls | ✅ | ✅ |
| Phone Calls | ✅ | ✅ |
| Call History | ✅ | ✅ |

## Development

### Python

```bash
cd sdk/python
pip install -e ".[dev]"
pytest
```

### JavaScript

```bash
cd sdk/javascript
npm install
npm run build
npm test
```

## License

MIT License
