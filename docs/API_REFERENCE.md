# Ragamuffin API Reference

Complete API documentation for the Ragamuffin platform.

## Base URLs

| Service | URL | Description |
|---------|-----|-------------|
| Backend API | `http://localhost:8000` | Main API gateway |
| RAG Service | `http://localhost:8001` | RAG operations |
| Swagger UI | `http://localhost:8000/docs` | Interactive API docs |

## Authentication

All protected endpoints require a JWT token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Register User

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": "uuid"
}
```

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Refresh Token

```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}
```

### Get Current User

```http
GET /auth/me
Authorization: Bearer <token>
```

---

## RAG Operations

### Embed Text Documents

```http
POST /rag/embed
Content-Type: multipart/form-data

texts: ["Document 1", "Document 2", ...]
collection_name: "my_collection"
```

**Response:**
```json
{
  "success": true,
  "count": 2,
  "collection": "my_collection"
}
```

### Embed Image

```http
POST /rag/embed_image
Content-Type: multipart/form-data

file: <image file>
collection_name: "image_collection"
```

### Vector Search

```http
POST /rag/search
Content-Type: multipart/form-data

text: "search query"
top_k: 5
collection_name: "my_collection"
```

**Response:**
```json
{
  "results": [
    {
      "id": "123",
      "text": "Matching document...",
      "score": 0.95
    }
  ]
}
```

### RAG Query

```http
POST /rag/query
Content-Type: multipart/form-data

query: "What is machine learning?"
top_k: 5
collection_name: "my_collection"
```

**Response:**
```json
{
  "response": "Machine learning is...",
  "context": [
    {"text": "Source document 1...", "score": 0.92},
    {"text": "Source document 2...", "score": 0.87}
  ]
}
```

### List Collections

```http
GET /rag/collections
Authorization: Bearer <token>
```

**Response:**
```json
{
  "collections": [
    {"name": "my_collection", "count": 100},
    {"name": "images", "count": 50}
  ]
}
```

---

## Flow Management

### Save Flow

```http
POST /save_flow/
Content-Type: multipart/form-data

flow_file: <JSON file>
```

### List Flows

```http
GET /list_flows/
```

**Response:**
```json
{
  "flows": ["flow1.json", "flow2.json"]
}
```

### Get Flow

```http
GET /get_flow/{flow_name}
```

### Run Flow

```http
POST /run_flow/
Content-Type: multipart/form-data

flow_file: <JSON file>
user_input: "Hello, AI!"
```

### Delete Flow

```http
DELETE /delete_flow/{flow_name}
```

---

## Voice (Retell.ai)

### Check Status

```http
GET /retell/status
```

### List Agents

```http
GET /retell/agents
Authorization: Bearer <token>
```

### Create Web Call

```http
POST /retell/web-call
Content-Type: multipart/form-data

agent_id: "agent_xxx"
```

**Response:**
```json
{
  "call_id": "call_xxx",
  "access_token": "..."
}
```

### Create Phone Call

```http
POST /retell/phone-call
Content-Type: multipart/form-data

agent_id: "agent_xxx"
to_number: "+1234567890"
```

### List Calls

```http
GET /retell/calls
Authorization: Bearer <token>
```

### Get Call Details

```http
GET /retell/calls/{call_id}
Authorization: Bearer <token>
```

### End Call

```http
POST /retell/end-call/{call_id}
Authorization: Bearer <token>
```

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Server Error |

---

## Rate Limiting

- **Default**: 100 requests/minute per IP
- **Auth endpoints**: 10 requests/minute
- **RAG embed**: 50 requests/minute

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699900000
```

---

## SDK Examples

### Python

```python
from ragamuffin import RagamuffinClient

client = RagamuffinClient("http://localhost:8000")
client.login("user@example.com", "password")

# Embed
client.rag.embed(["Doc 1", "Doc 2"])

# Search
results = client.rag.search("query", top_k=5)

# RAG Query
response = client.rag.query("What is AI?")
```

### JavaScript

```typescript
import { RagamuffinClient } from '@ragamuffin/sdk';

const client = new RagamuffinClient('http://localhost:8000');
await client.login('user@example.com', 'password');

// Embed
await client.rag.embed(['Doc 1', 'Doc 2']);

// Search
const results = await client.rag.search('query', { topK: 5 });

// RAG Query
const response = await client.rag.query('What is AI?');
```

---

## See Also

- [Architecture Guide](./ARCHITECTURE.md)
- [Security Guide](../SECURITY.md)
- [Production Guide](../PRODUCTION.md)
