# rag7

Production-ready RAG (Retrieval-Augmented Generation) application with LangGraph, n8n orchestration, and comprehensive deployment templates.

## 🚀 Quick Start

This repository now includes production-ready deployment templates for moving from prototype to production:

- **CI/CD Workflows**: Automated testing, linting, and Docker image builds
- **Docker Compose**: Production deployment with PostgreSQL, Redis, LangGraph, and n8n
- **Kubernetes Manifests**: K8s deployments with auto-scaling and health checks
- **n8n Workflows**: Pre-built automation workflows for LangGraph orchestration
- **Documentation**: Comprehensive guides for deployment, observability, and incident response

## 📚 Documentation

- [Deployment Guide](docs/deployment.md) - Deploy using Docker Compose or Kubernetes
- [Observability Guide](docs/observability.md) - Monitoring, metrics, and tracing
- [Incident Runbook](docs/runbook.md) - Troubleshooting and incident response
- [n8n Workflows](n8n/README.md) - Automation workflow setup and usage

## 🛠️ Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- kubectl (for Kubernetes deployment)
- GitHub Container Registry access token

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/Stacey77/rag7.git
cd rag7
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.prod.example .env.prod
# Edit .env.prod with your configuration
```

### Production Deployment

See the [Deployment Guide](docs/deployment.md) for detailed instructions.

**Quick Deploy with Docker Compose:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

**Deploy to Kubernetes:**
```bash
kubectl apply -f k8s/
```

## 📁 Project Structure

```
rag7/
├── .github/workflows/     # CI/CD workflows
├── docs/                  # Documentation
├── integration/api/       # LangGraph API server
├── k8s/                   # Kubernetes manifests
├── n8n/                   # n8n workflows and setup
├── .env.prod.example      # Environment variables template
├── docker-compose.prod.yml # Production Docker Compose
├── pyproject.toml         # Python project metadata
└── requirements.txt       # Development dependencies
```

## 🔐 Security

Please see [SECURITY.md](SECURITY.md) for our security policy and how to report vulnerabilities.

## 📝 License

MIT