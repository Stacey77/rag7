# RAG7 - AI Product Platform

A comprehensive platform for designing, building, and deploying LLM-powered AI products for enterprise clients. RAG7 enables rapid iteration on customer data with real-time feedback, supporting multi-LLM and multi-agent AI systems.

## 🚀 Features

### Core Capabilities
- **Multi-LLM Support**: Integrate with OpenAI, Anthropic Claude, and other LLM providers
- **Multi-Agent Orchestration**: Coordinate specialized AI agents for complex workflows
- **RAG (Retrieval-Augmented Generation)**: Build knowledge-driven AI systems
- **Vector Database Integration**: Support for Pinecone, Weaviate, and ChromaDB
- **Real-Time Monitoring**: Track performance, costs, and metrics in production
- **Enterprise Security**: Built-in authentication, authorization, and audit logging

### Development Platform
- **FastAPI Backend**: High-performance async API server
- **REST API**: Comprehensive API for all platform features
- **Docker Support**: Containerized deployment with Docker Compose
- **Scalable Architecture**: Designed for production workloads

### Deployment & Operations
- **Multi-Environment**: Development, staging, and production deployments
- **Auto-Scaling**: Automatic scaling based on load
- **Metrics & Logging**: Prometheus metrics and structured logging
- **CI/CD Ready**: Prepared for continuous integration and deployment

## 📋 Prerequisites

- Python 3.11+
- Docker and Docker Compose (optional, for containerized deployment)
- API keys for LLM providers (OpenAI, Anthropic, etc.)
- Vector database access (Pinecone, Weaviate, or ChromaDB)

## 🛠️ Installation

### Option 1: Local Development

1. **Clone the repository**:
```bash
git clone https://github.com/Stacey77/rag7.git
cd rag7
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. **Run the application**:
```bash
python -m app.main
```

### Option 2: Docker Deployment

1. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

2. **Start services**:
```bash
docker-compose up -d
```

3. **Access the API**:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

## 📖 Quick Start

### 1. Create an AI Project

```bash
curl -X POST "http://localhost:8000/api/v1/projects/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Support AI",
    "description": "AI-powered customer support system",
    "customer_id": "customer_123",
    "use_case": "customer_support",
    "llm_providers": ["openai"]
  }'
```

### 2. Generate LLM Completion

```bash
curl -X POST "http://localhost:8000/api/v1/llm/completion" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms",
    "provider": "openai",
    "temperature": 0.7
  }'
```

### 3. Execute Multi-Agent Workflow

```bash
curl -X POST "http://localhost:8000/api/v1/agents/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "research",
    "instruction": "Research latest trends in AI",
    "max_iterations": 5
  }'
```

### 4. Deploy to Production

```bash
curl -X POST "http://localhost:8000/api/v1/deployments/" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj_001",
    "environment": "production",
    "config": {"replicas": 3, "auto_scaling": true}
  }'
```

## 🏗️ Architecture

### Directory Structure

```
rag7/
├── app/
│   ├── api/              # API endpoints and routes
│   │   └── endpoints/    # Endpoint modules (llm, agents, projects, deployments)
│   ├── core/            # Core configuration and utilities
│   ├── models/          # Data models
│   ├── services/        # Business logic services
│   │   ├── llm_service.py      # Multi-LLM integration
│   │   └── rag_service.py      # RAG operations
│   ├── agents/          # AI agent implementations
│   └── utils/           # Utility functions
├── tests/               # Test suite
├── docker/              # Docker configuration
├── docs/                # Additional documentation
├── scripts/             # Setup and deployment scripts
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── docker-compose.yml   # Docker Compose configuration
```

### Key Components

1. **API Layer**: FastAPI-based REST API with OpenAPI documentation
2. **LLM Service**: Unified interface for multiple LLM providers
3. **RAG Service**: Document ingestion and retrieval-augmented generation
4. **Agent System**: Multi-agent orchestration for complex tasks
5. **Deployment Manager**: Production deployment and scaling
6. **Monitoring**: Prometheus metrics and structured logging

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example` for full list):

```bash
# LLM Providers
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Vector Databases
PINECONE_API_KEY=your_pinecone_key
WEAVIATE_URL=http://localhost:8080

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/rag7

# Security
SECRET_KEY=your_secret_key_change_in_production
```

## 📚 API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Main Endpoints

- `/api/v1/llm/*` - LLM interactions (completions, chat)
- `/api/v1/agents/*` - Agent execution and orchestration
- `/api/v1/projects/*` - Project management
- `/api/v1/deployments/*` - Deployment operations

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_llm_service.py
```

## 🚢 Production Deployment

### Docker Production Build

```bash
# Build production image
docker build -t rag7:latest .

# Run production container
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name rag7-api \
  rag7:latest
```

### Kubernetes Deployment

See `docs/kubernetes.md` for Kubernetes deployment guides.

## 📊 Monitoring

### Metrics

Prometheus metrics are exposed at `/metrics`:
- Request rates and latencies
- Error rates
- LLM usage and costs
- Deployment health

### Logging

Structured JSON logs with levels:
- INFO: General operations
- WARNING: Potential issues
- ERROR: Errors and exceptions

Logs are stored in `logs/` directory with daily rotation.

## 🔒 Security

- API key authentication
- Rate limiting
- Request validation
- Audit logging
- Environment-based secrets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

See LICENSE file for details.

## 🆘 Support

For issues and questions:
- GitHub Issues: https://github.com/Stacey77/rag7/issues
- Documentation: See `docs/` directory

## 🎯 Roadmap

- [ ] Additional LLM provider integrations
- [ ] Advanced agent workflows with LangGraph
- [ ] Fine-tuning pipeline
- [ ] Model evaluation framework
- [ ] Enhanced monitoring dashboard
- [ ] Multi-tenancy support

---

Built for enterprise AI product development with ❤️