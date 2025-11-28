# Ragamuffin Architecture Guide

System architecture and design documentation for the Ragamuffin platform.

## Overview

Ragamuffin is a microservices-based AI orchestration platform designed for enterprise RAG applications.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Load Balancer / Nginx                       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│   Frontend    │         │    Backend    │         │  RAG Service  │
│   (React)     │◄───────►│   (FastAPI)   │◄───────►│   (FastAPI)   │
│   Port 8080   │         │   Port 8000   │         │   Port 8001   │
└───────────────┘         └───────────────┘         └───────────────┘
                                    │                           │
                                    │                           │
        ┌───────────────────────────┼───────────────────────────┤
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│   LangFlow    │         │     n8n       │         │    Milvus     │
│   Port 7860   │         │   Port 5678   │         │   Port 19530  │
└───────────────┘         └───────────────┘         └───────────────┘
                                                            │
                                    ┌───────────────────────┴───────┐
                                    │                               │
                                    ▼                               ▼
                          ┌───────────────┐               ┌───────────────┐
                          │     MinIO     │               │     Etcd      │
                          │   Port 9000   │               │   Port 2379   │
                          └───────────────┘               └───────────────┘
```

## Services

### Frontend (React + TypeScript)

**Purpose**: Web UI for platform interaction

**Features**:
- Dashboard with metrics
- RAG query interface
- Document management
- Flow builder
- Voice calls (Retell.ai)
- User authentication

**Tech Stack**:
- Vite + React 18
- TypeScript
- React Router
- Cyberpunk theme (Orbitron font)

### Backend API (FastAPI)

**Purpose**: Main API gateway and orchestration

**Features**:
- JWT authentication
- Rate limiting
- Flow management (CRUD)
- RAG endpoint proxying
- Retell.ai integration
- Request logging

**Tech Stack**:
- FastAPI
- Python 3.10+
- Pydantic
- python-jose (JWT)
- slowapi (rate limiting)

### RAG Service (FastAPI)

**Purpose**: Multimodal embedding and retrieval

**Features**:
- Text embedding (sentence-transformers)
- Image embedding
- Vector search
- Hybrid search (dense + sparse)
- Document chunking
- Result reranking (MMR)

**Tech Stack**:
- FastAPI
- sentence-transformers
- pymilvus
- rank-bm25
- scikit-learn

### LangFlow

**Purpose**: Visual AI flow design

**Features**:
- Drag-and-drop flow builder
- Component library
- Flow execution
- LLM integrations

### n8n

**Purpose**: Workflow automation

**Features**:
- Visual workflow builder
- Scheduled tasks
- Webhook triggers
- API integrations
- Document pipelines

### Milvus

**Purpose**: Vector database

**Features**:
- High-performance similarity search
- IVF_FLAT indexing
- Multiple collections
- Horizontal scaling

**Dependencies**:
- MinIO (object storage)
- Etcd (metadata)

---

## Data Flow

### RAG Query Flow

```
1. User submits query
        │
        ▼
2. Backend receives request
        │
        ▼
3. Backend forwards to RAG Service
        │
        ▼
4. RAG Service generates query embedding
        │
        ▼
5. Milvus performs vector search
        │
        ▼
6. RAG Service retrieves top-k results
        │
        ▼
7. (Optional) Hybrid search with BM25
        │
        ▼
8. (Optional) Rerank with MMR
        │
        ▼
9. Return context and response
```

### Document Embedding Flow

```
1. User uploads documents
        │
        ▼
2. Backend receives documents
        │
        ▼
3. Backend forwards to RAG Service
        │
        ▼
4. RAG Service chunks documents
        │
        ▼
5. RAG Service generates embeddings
        │
        ▼
6. Milvus stores vectors
        │
        ▼
7. Return success response
```

---

## Security Model

### Authentication

- JWT tokens (access + refresh)
- bcrypt password hashing
- Token expiration (30 min access, 7 day refresh)

### Authorization

- Role-based access (future)
- API key authentication (future)
- Protected routes

### Rate Limiting

- Per-IP limits
- Endpoint-specific limits
- Burst handling

### Security Headers

- HSTS
- X-Frame-Options
- X-Content-Type-Options
- CSP

---

## Scaling Considerations

### Horizontal Scaling

| Component | Strategy |
|-----------|----------|
| Frontend | CDN + load balancing |
| Backend | Multiple instances + load balancer |
| RAG Service | Multiple instances |
| Milvus | Cluster mode |
| n8n | Queue-based workers |

### Caching

- Redis for session/token caching
- Result caching for repeated queries
- Embedding cache for common documents

### Performance

- Async processing for embeddings
- Batch operations
- Connection pooling
- Index optimization

---

## Deployment

### Development

```bash
./start-dev.sh
```

### Staging

```bash
./deploy-staging.sh --build
```

### Production

See [PRODUCTION.md](../PRODUCTION.md) for:
- Kubernetes deployment
- SSL/TLS setup
- Database configuration
- Monitoring setup
- Backup strategies

---

## Directory Structure

```
ragamuffin/
├── langflow-backend/          # Backend API
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── auth.py           # Authentication
│   │   ├── models.py         # Pydantic models
│   │   ├── middleware.py     # Rate limiting
│   │   └── retell.py         # Voice integration
│   ├── flows/                # Saved flows
│   └── tests/                # Backend tests
│
├── rag-service/              # RAG Service
│   ├── app/
│   │   ├── main.py          # RAG API
│   │   ├── chunking.py      # Document chunking
│   │   ├── hybrid_search.py # Hybrid search
│   │   └── reranking.py     # MMR reranking
│   └── tests/               # RAG tests
│
├── web-client/              # Frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   └── contexts/        # React contexts
│   └── __tests__/           # Frontend tests
│
├── sdk/                     # Client SDKs
│   ├── python/             # Python SDK
│   └── javascript/         # JS/TS SDK
│
├── n8n-workflows/          # Workflow templates
├── examples/               # Tutorials
├── docs/                   # Documentation
└── .github/                # CI/CD workflows
```

---

## See Also

- [API Reference](./API_REFERENCE.md)
- [Security Guide](../SECURITY.md)
- [Production Guide](../PRODUCTION.md)
- [Deployment Checklist](../DEPLOYMENT_CHECKLIST.md)
