# Ragamuffin Platform

![Ragamuffin UI Inspiration](<img>)

**Ragamuffin** is an advanced AI orchestration platform that combines LangFlow for visual flow design, a FastAPI backend for flow management and execution, multimodal RAG with Milvus vector database, n8n workflow automation, and a modern React + TypeScript web interface with a cyberpunk-inspired design.

## Project Name
**Ragamuffin** - A powerful monorepo platform for building, managing, and deploying AI agent workflows with multimodal RAG capabilities.

## Architecture Overview
This monorepo contains eight main components:
- **LangFlow Container**: Visual AI flow designer (port 7860)
- **FastAPI Backend**: Flow persistence and execution API (port 8000)
- **RAG Service**: Multimodal RAG with Milvus integration (port 8001)
- **Milvus**: Vector database for embeddings (port 19530)
- **n8n**: Workflow automation platform (port 5678)
- **MinIO**: Object storage for Milvus (port 9000/9001)
- **Etcd**: Metadata storage for Milvus (port 2379)
- **Web Client**: React + TypeScript frontend with Vite (port 8080)

## Quick Start
```bash
# Start all services (includes Milvus, n8n, RAG)
./start-dev.sh

# Stop all services
./stop-dev.sh
```

## Access Points
- **Frontend**: http://localhost:8080 - Main UI with RAG interface
- **Backend API**: http://localhost:8000 - Flow & RAG API
- **RAG Service**: http://localhost:8001 - Multimodal RAG API
- **LangFlow UI**: http://localhost:7860 - Flow designer
- **n8n**: http://localhost:5678 - Workflow automation (admin/admin)
- **MinIO Console**: http://localhost:9001 - Object storage (minioadmin/minioadmin)
- **Milvus**: localhost:19530 - Vector database

## Features

### Multimodal RAG
- **Text Embedding**: Generate and search text embeddings
- **Image Embedding**: Process and search images
- **Document Processing**: PDF and document support
- **Vector Search**: Fast similarity search with Milvus
- **Hybrid Retrieval**: Combine multiple modalities

### Frontend UI (NEW!)
- **RAG Query Page**: Interactive RAG query and vector search interface
- **Documents Page**: Embed and manage text documents and images
- **Dashboard**: System overview and metrics
- **Playground**: Conversation interface
- **Datasets**: Dataset management
- **Agent Builder**: Flow design and execution

### Workflow Automation
- **n8n Integration**: Visual workflow builder
- **API Automation**: Connect RAG with external services
- **Scheduled Tasks**: Automate embedding generation

### Flow Management
- **Visual Design**: LangFlow for agent workflows
- **Persistence**: Save and version flows
- **Execution**: Run flows with context

## Staging Deployment

Deploy to staging environment with the included scripts:

```bash
# 1. Copy and configure staging environment
cp .env.staging.example .env.staging
# Edit .env.staging with your credentials

# 2. Run deployment checklist
./deploy-staging.sh --checklist

# 3. Deploy to staging
./deploy-staging.sh --build

# 4. Check status
./deploy-staging.sh --status

# 5. View logs
./deploy-staging.sh --logs
```

See [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) for complete deployment guide.

## Production Deployment

For production environments, follow the comprehensive guides:

1. **Security**: Review [SECURITY.md](./SECURITY.md) for security checklist
2. **Production**: Follow [PRODUCTION.md](./PRODUCTION.md) for deployment
3. **Checklist**: Complete [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)

Key production requirements:
- Change all default passwords
- Generate secure JWT secret: `openssl rand -hex 32`
- Configure HTTPS/TLS with certificates
- Set up PostgreSQL for user data
- Configure proper CORS origins
- Enable monitoring and alerting

## Security Features

The platform includes production-ready security:

- **JWT Authentication**: Token-based auth with refresh tokens
- **Rate Limiting**: Per-IP rate limiting with slowapi
- **Input Validation**: Pydantic models for all endpoints
- **Security Headers**: HSTS, X-Frame-Options, CSP
- **Request Logging**: Unique request IDs, structured logging
- **Password Hashing**: bcrypt for secure password storage

## Advanced RAG Features

- **Document Chunking**: Multiple strategies (character, sentence, separator)
- **Hybrid Search**: Dense + BM25 sparse retrieval with RRF fusion
- **Result Reranking**: MMR for diversity, phrase boosting
- **Collection Management**: Multiple embedding collections

## Documentation

- [README_MONOREPO.md](./README_MONOREPO.md) - Detailed monorepo structure
- [RUN_COMMANDS.md](./RUN_COMMANDS.md) - Comprehensive run instructions
- [SECURITY.md](./SECURITY.md) - Security guidelines and checklist
- [PRODUCTION.md](./PRODUCTION.md) - Production deployment guide
- [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - Pre-deployment checklist
- [rag-service/README.md](./rag-service/README.md) - RAG service details

## UI Inspiration
The web client features a cyberpunk-inspired design with the Orbitron font and modern React components:

![UI Reference](<img>)

## Support

For issues and questions:
- Review documentation in this repository
- Check [SECURITY.md](./SECURITY.md) for security concerns
- Check [PRODUCTION.md](./PRODUCTION.md) for deployment issues