# RAG7 ADK Multi-Agent System

[![CI Status](https://github.com/Stacey77/rag7/workflows/CI%20-%20Build%20and%20Test/badge.svg)](https://github.com/Stacey77/rag7/actions)
[![Docker Build](https://github.com/Stacey77/rag7/workflows/Docker%20-%20Build%20and%20Push/badge.svg)](https://github.com/Stacey77/rag7/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A production-ready multi-agent system built with Agent Development Kit (ADK), featuring RAG capabilities, LiteLLM multi-model integration, and comprehensive observability.

## 🌟 Features

- **Multi-Agent Orchestration**: Scalable agent architecture with intelligent task distribution
- **LiteLLM Integration**: Unified interface for Gemini, GPT-4, Claude, and Mistral models
- **Smart Model Routing**: Cost and performance-optimized model selection
- **Production Ready**: Complete CI/CD pipelines, containerization, and deployment configs
- **Observability**: Prometheus metrics, Jaeger tracing, and structured logging
- **Resilience**: Circuit breakers, retries, fallbacks, and chaos testing
- **Security**: Vulnerability scanning, secret management, and PII redaction

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Google Cloud Platform account (for deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Stacey77/rag7.git
   cd rag7
   ```

2. **Set up environment**
   ```bash
   make local-setup
   # Edit .env file with your API keys
   ```

3. **Install dependencies**
   ```bash
   make install-dev
   ```

4. **Start services with Docker Compose**
   ```bash
   make docker-up
   ```

5. **Access the services**
   - API: http://localhost:8080
   - Prometheus: http://localhost:9091
   - Grafana: http://localhost:3000 (admin/admin)
   - Jaeger: http://localhost:16686
   - LiteLLM Proxy: http://localhost:4000

## 📋 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  Load Balancer │
                    │  (Ingress)     │
                    └───────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    ┌───▼────┐         ┌────▼───┐         ┌────▼───┐
    │ Agent  │         │ Agent  │         │ Agent  │
    │ API 1  │         │ API 2  │         │ API 3  │
    └───┬────┘         └────┬───┘         └────┬───┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    ┌───▼──────┐    ┌──────▼─────┐    ┌───────▼────┐
    │ LiteLLM  │    │   Redis    │    │ PostgreSQL │
    │  Proxy   │    │  (Cache)   │    │    (DB)    │
    └──────────┘    └────────────┘    └────────────┘
                            │
                    ┌───────▼────────┐
                    │     Qdrant     │
                    │  (Vector DB)   │
                    └────────────────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed system design.

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test types
make test-unit
make test-integration
make test-orchestration
make test-chaos

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 🔧 Development

```bash
# Format code
make format

# Run linters
make lint

# Type checking
make type-check

# Security scan
make security-check

# Run locally
make run-local
```

## 📦 Deployment

### Cloud Run
```bash
make deploy-dev
make deploy-staging
make deploy-prod
```

### GKE
```bash
# Deploy to dev
kubectl apply -k deploy/gke/overlays/dev

# Deploy to prod
kubectl apply -k deploy/gke/overlays/prod
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment guides.

## 📊 Monitoring

- **Metrics**: Prometheus scrapes metrics from `/metrics` endpoint
- **Dashboards**: Pre-configured Grafana dashboards
- **Tracing**: Distributed tracing with Jaeger
- **Logging**: Structured JSON logs with PII redaction

## 🔐 Security

- Multi-stage Docker builds with non-root users
- Dependency vulnerability scanning (Trivy, Bandit)
- Secret scanning with Gitleaks
- SBOM generation with Syft
- Image signing with Cosign

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and components
- [Deployment](docs/DEPLOYMENT.md) - Deployment guides and runbooks
- [Development](docs/DEVELOPMENT.md) - Development setup and guidelines

## 📄 License

This project is licensed under the MIT License.

---

Made with ❤️ by the RAG7 Team