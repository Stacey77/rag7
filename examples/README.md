# Ragamuffin Examples

This directory contains example code and Jupyter notebooks to help you get started with the Ragamuffin platform.

## 📓 Jupyter Notebooks

Interactive tutorials covering all platform features:

| Notebook | Description |
|----------|-------------|
| `01_getting_started.ipynb` | Platform setup and first RAG query |
| `02_rag_operations.ipynb` | Embedding, search, and RAG queries |
| `03_advanced_rag.ipynb` | Chunking, hybrid search, reranking |

## 🚀 Quick Start

### Prerequisites

1. Ragamuffin platform running:
   ```bash
   ./start-dev.sh
   ```

2. Install notebook requirements:
   ```bash
   cd examples/notebooks
   pip install -r requirements.txt
   ```

3. Start Jupyter:
   ```bash
   jupyter notebook
   ```

### Using the Python SDK

```python
from ragamuffin import RagamuffinClient

# Initialize client
client = RagamuffinClient("http://localhost:8000")

# Authenticate
client.login("user@example.com", "password")

# Embed documents
client.rag.embed(["Document 1", "Document 2"])

# Search
results = client.rag.search("query", top_k=5)

# RAG query
response = client.rag.query("What is machine learning?")
```

### Using the JavaScript SDK

```typescript
import { RagamuffinClient } from '@ragamuffin/sdk';

const client = new RagamuffinClient('http://localhost:8000');
await client.login('user@example.com', 'password');

// Embed documents
await client.rag.embed(['Document 1', 'Document 2']);

// Search
const results = await client.rag.search('query', { topK: 5 });

// RAG query
const response = await client.rag.query('What is machine learning?');
```

## 📖 Additional Resources

- [API Reference](../docs/API_REFERENCE.md) - Complete API documentation
- [Architecture Guide](../docs/ARCHITECTURE.md) - System design overview
- [Python SDK](../sdk/python/README.md) - Python client library
- [JavaScript SDK](../sdk/javascript/README.md) - JavaScript/TypeScript client library
- [Security Guide](../SECURITY.md) - Security best practices
- [Production Guide](../PRODUCTION.md) - Deployment instructions
