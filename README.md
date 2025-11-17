# 🛡️ FortFail - Backup & Restore Orchestrator (PoC)

A proof-of-concept implementation of a distributed backup and restore orchestration system with agent-based architecture.

## 🎯 Overview

FortFail provides a complete backup and restore solution with:

- **Orchestrator**: Central FastAPI-based service managing snapshots, restore jobs, and agent coordination
- **Agent**: Autonomous backup/restore agents that register with the orchestrator
- **Dashboard**: React-based web UI for monitoring and control
- **Real-time Events**: WebSocket streaming for live system monitoring
- **S3 Storage**: MinIO/S3-compatible object storage for snapshots
- **Write-Ahead Log**: Persistent audit trail of all operations

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────┐
│  Dashboard  │────▶│ Orchestrator │────▶│  MinIO  │
└─────────────┘     └──────────────┘     └─────────┘
                           │                    │
                           │                    │
                           ▼                    ▼
                    ┌────────────┐      ┌──────────┐
                    │ PostgreSQL │      │ Snapshots│
                    └────────────┘      └──────────┘
                           ▲
                           │
                    ┌──────┴──────┐
                    │             │
                ┌───▼───┐     ┌───▼───┐
                │Agent 1│     │Agent 2│
                └───────┘     └───────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- curl and jq (for smoke test)

### Run Locally

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Stacey77/rag7.git
   cd rag7
   ```

2. **Set environment variables** (optional):
   ```bash
   export ORCH_JWT_SECRET="your-strong-secret-here"
   export ORCH_REG_SECRET="your-registration-secret-here"
   ```

3. **Start all services**:
   ```bash
   docker-compose up --build
   ```

4. **Access the services**:
   - Orchestrator API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Control UI: http://localhost:8000/control
   - MinIO Console: http://localhost:9001 (admin/minioadmin)

5. **Run smoke test**:
   ```bash
   ./scripts/smoke.sh
   ```

### Build Dashboard Separately

```bash
cd dashboard
npm install
npm start  # Dev server on http://localhost:1234
npm build  # Production build
```

## 📋 Components

### Orchestrator (`orchestrator/`)

Central service providing REST API and WebSocket endpoints:

- **Authentication**: JWT-based token management
- **Snapshots**: Metadata storage and S3 upload/download
- **Restore Jobs**: Job creation and tracking
- **Agent Management**: Agent registration and command dispatch
- **Real-time Events**: WebSocket broadcasting
- **Health Checks**: Liveness and readiness probes

**Key Files**:
- `main.py`: FastAPI application with all endpoints
- `ws.py`: WebSocket manager
- `ui/control.html`: Static control panel
- `openapi.yaml`: OpenAPI specification

### Agent (`agent/`)

Autonomous agent that:

- Bootstraps JWT authentication
- Creates and uploads snapshots (tar archives)
- Polls for commands from orchestrator
- Executes restore operations
- Reports events back to orchestrator

**Key Files**:
- `agent.py`: Agent implementation
- `k8s/agent-deployment.yaml`: Kubernetes manifest

### Dashboard (`dashboard/`)

Modern React-based UI with:

- Token authentication
- Agent listing
- Restore job creation
- Job status monitoring
- Live event streaming

**Tech Stack**: React 18, Parcel, WebSocket API

## 🔐 Security Notes

⚠️ **This is a PoC Implementation**

### Production Considerations

1. **Secrets Management**:
   - Use environment variables (never commit secrets!)
   - Consider Vault, AWS Secrets Manager, or similar
   - Rotate secrets regularly

2. **Network Security**:
   - Enable HTTPS/TLS for all communications
   - Use mutual TLS between agents and orchestrator
   - Restrict CORS origins in production

3. **Access Control**:
   - Implement role-based access control (RBAC)
   - Add rate limiting and request throttling
   - Enable audit logging

4. **Data Security**:
   - Encrypt snapshots at rest and in transit
   - Implement data retention policies
   - Secure S3 bucket policies

5. **Input Validation**:
   - Validate all user inputs
   - Sanitize file paths in tar extraction
   - Implement checksum verification

### Default Secrets (⚠️ Change in Production!)

```bash
ORCH_JWT_SECRET=dev-jwt-secret-change-in-production
ORCH_REG_SECRET=dev-reg-secret-change-in-production
```

## 🔧 Configuration

All services are configured via environment variables:

### Orchestrator

| Variable | Description | Default |
|----------|-------------|---------|
| `ORCH_JWT_SECRET` | JWT signing secret | `dev-jwt-secret-change-in-production` |
| `ORCH_REG_SECRET` | Registration secret | `dev-reg-secret-change-in-production` |
| `DATABASE_URL` | PostgreSQL connection string | `sqlite:///./orchestrator.db` |
| `S3_ENDPOINT` | S3/MinIO endpoint | `http://minio:9000` |
| `S3_ACCESS_KEY` | S3 access key | `minioadmin` |
| `S3_SECRET_KEY` | S3 secret key | `minioadmin` |
| `S3_BUCKET` | Bucket name | `fortfail-snapshots` |
| `WAL_PATH` | Write-ahead log path | `/data/orchestrator_wal.log` |
| **Production Features** | | |
| `SECRETS_BACKEND` | Secrets backend (env/aws/vault) | `env` |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins (comma-separated) | `*` |
| `RATE_LIMIT_ENABLED` | Enable rate limiting | `true` |
| `RATE_LIMIT_PER_MINUTE` | Requests per minute per IP | `60` |
| `TLS_ENABLED` | Enable HTTPS/TLS | `false` |
| `TLS_CERT_FILE` | Path to TLS certificate | - |
| `TLS_KEY_FILE` | Path to TLS private key | - |
| `TLS_CA_FILE` | Path to CA certificate (optional) | - |

#### Secrets Management

FortFail supports multiple secrets backends:

**Environment Variables** (default):
```bash
export ORCH_JWT_SECRET="your-secret"
```

**AWS Secrets Manager**:
```bash
export SECRETS_BACKEND=aws
export ORCH_JWT_SECRET="fortfail/production:jwt_secret"
```

**HashiCorp Vault**:
```bash
export SECRETS_BACKEND=vault
export VAULT_ADDR="https://vault.example.com"
export VAULT_TOKEN="your-token"
export ORCH_JWT_SECRET="fortfail/orchestrator:jwt_secret"
```
| `WAL_PATH` | Write-ahead log path | `/data/orchestrator_wal.log` |

### Agent

| Variable | Description | Default |
|----------|-------------|---------|
| `ORCHESTRATOR_URL` | Orchestrator endpoint | `http://orchestrator:8000` |
| `AGENT_ID` | Unique agent identifier | `agent-{pid}` |
| `AGENT_REG_SECRET` | Registration secret | `dev-reg-secret-change-in-production` |
| `ORCH_JWT` | Pre-provisioned JWT (optional) | - |
| `BACKUP_DIR` | Backup source directory | `/backups` |
| `RESTORE_DIR` | Restore target directory | `/restore` |
| `POLL_INTERVAL` | Command poll interval (seconds) | `10` |

## 🧪 Testing

### Smoke Test

The `scripts/smoke.sh` script performs end-to-end testing:

1. Wait for orchestrator readiness
2. Obtain JWT token
3. Create and upload test snapshot
4. Create restore job
5. Verify command queued for agent
6. Check job status
7. List agents

**Dependencies**: `curl`, `jq`

```bash
./scripts/smoke.sh
```

## 📦 Deployment

### Docker Compose (Local/Dev)

```bash
docker-compose up --build
```

### Kubernetes

```bash
# Create secrets
kubectl create secret generic fortfail-secrets \
  --from-literal=jwt-secret=your-jwt-secret \
  --from-literal=reg-secret=your-reg-secret \
  --from-literal=db-password=your-db-password

# Deploy orchestrator
kubectl apply -f k8s/orchestrator-deployment.yaml

# Deploy agents
kubectl apply -f agent/k8s/agent-deployment.yaml
```

## 📚 API Reference

See the interactive API documentation at http://localhost:8000/docs

### Key Endpoints

- `POST /auth/token` - Obtain JWT token
- `POST /snapshots` - Create snapshot metadata
- `POST /snapshots/{id}/object` - Upload snapshot
- `GET /snapshots/{id}/object` - Download snapshot
- `POST /restore-jobs` - Create restore job
- `GET /restore-jobs/{id}` - Get job status
- `GET /agents` - List agents
- `GET /agent/{id}/commands` - Get pending commands
- `POST /agent/{id}/events` - Post agent event
- `WS /ws` - WebSocket event stream

## 🚀 Production Features

### ✅ Implemented

1. **Secrets Management**
   - Support for AWS Secrets Manager
   - Support for HashiCorp Vault
   - Fallback to environment variables

2. **Security Enhancements**
   - HTTPS/TLS support with configurable certificates
   - Rate limiting (60 requests/minute per IP by default)
   - Enhanced input validation with Pydantic
   - Configurable CORS origins

3. **CI/CD Pipeline**
   - Automated testing and linting
   - Security scanning with Trivy
   - Docker image builds and publishing
   - Integration tests with smoke test
   - Staging and production deployment workflows

4. **Scaling Support**
   - Multi-orchestrator architecture
   - Load balancer configurations (nginx, HAProxy)
   - Kubernetes HPA support
   - Database read replicas
   - See [docs/SCALING.md](docs/SCALING.md) for details

### Production Deployment Checklist

- [ ] Configure strong secrets (not default placeholders)
- [ ] Enable TLS/HTTPS with valid certificates
- [ ] Set specific CORS allowed origins
- [ ] Configure secrets backend (Vault/AWS Secrets Manager)
- [ ] Set up database backups and replication
- [ ] Configure monitoring and alerting
- [ ] Review and adjust rate limits
- [ ] Set up load balancer with session affinity
- [ ] Enable audit logging
- [ ] Configure firewall rules and network segmentation

## 🤝 Contributing

This is a PoC. For production use:

1. Implement comprehensive testing
2. Add monitoring and alerting
3. Enhance error handling
4. Implement proper secrets management
5. Add authentication/authorization
6. Performance optimization
7. Security hardening

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🔗 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [MinIO Documentation](https://min.io/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**⚠️ Warning**: This is a proof-of-concept implementation. Do not use in production without proper security hardening and testing.