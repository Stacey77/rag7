# Deployment Guide

This guide covers deploying the LangGraph Multi-Agent System with n8n integration.

## Quick Start (Docker)

The fastest way to get started:

```bash
# Clone the repository
git clone https://github.com/your-org/rag7.git
cd rag7

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps
```

**Access Points:**
- LangGraph API: http://localhost:8000
- n8n Dashboard: http://localhost:5678
- API Documentation: http://localhost:8000/docs

## Prerequisites

### Required
- Docker >= 20.10
- Docker Compose >= 2.0
- OpenAI API key

### Optional
- Python 3.11+ (for local development)
- PostgreSQL client (for database management)
- Redis CLI (for cache inspection)

## Configuration

### Environment Variables

Create `.env` from the template:

```bash
cp .env.example .env
```

**Required Variables:**

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `secure_password` |
| `N8N_BASIC_AUTH_PASSWORD` | n8n admin password | `admin_password` |

**Optional Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `LANGGRAPH_API_PORT` | 8000 | API server port |
| `N8N_PORT` | 5678 | n8n dashboard port |
| `QUALITY_THRESHOLD` | 0.8 | Default quality threshold |
| `AGENT_MAX_ITERATIONS` | 10 | Maximum loop iterations |

### Sample Production Configuration

```bash
# .env for production
OPENAI_API_KEY=sk-your-production-key

# API Configuration
LANGGRAPH_API_HOST=0.0.0.0
LANGGRAPH_API_PORT=8000

# Database (use strong passwords)
POSTGRES_USER=langgraph
POSTGRES_PASSWORD=your-secure-password-here
POSTGRES_DB=n8n_production

# n8n Configuration
N8N_HOST=n8n.yourdomain.com
N8N_PROTOCOL=https
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your-secure-password-here
WEBHOOK_URL=https://n8n.yourdomain.com

# Agent Settings
QUALITY_THRESHOLD=0.85
AGENT_MAX_ITERATIONS=15

# Monitoring (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_PROJECT=production-agents
```

## Deployment Options

### 1. Docker Compose (Recommended)

**Full Stack Deployment:**

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Service-Specific Commands:**

```bash
# Start only LangGraph API
docker-compose up -d langgraph-api redis

# Start only n8n
docker-compose up -d n8n postgres

# Restart a specific service
docker-compose restart langgraph-api
```

### 2. Kubernetes

**Sample Kubernetes Deployment:**

```yaml
# langgraph-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langgraph-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: langgraph-api
  template:
    metadata:
      labels:
        app: langgraph-api
    spec:
      containers:
      - name: langgraph-api
        image: your-registry/langgraph-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: langgraph-secrets
              key: openai-api-key
        - name: REDIS_URL
          value: "redis://redis-service:6379/0"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: langgraph-api
spec:
  selector:
    app: langgraph-api
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### 3. Local Development

**Python Virtual Environment:**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Start Redis (required)
docker run -d -p 6379:6379 redis:7-alpine

# Start API server
python -m integration.api.server

# Or run CLI
python -m langgraph.main --list
```

## Service Architecture

### Production Topology

```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    │   (nginx/ALB)   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │LangGraph │   │LangGraph │   │LangGraph │
        │  API #1  │   │  API #2  │   │  API #3  │
        └────┬─────┘   └────┬─────┘   └────┬─────┘
             │              │              │
             └──────────────┼──────────────┘
                            │
                  ┌─────────┴─────────┐
                  │                   │
                  ▼                   ▼
            ┌──────────┐        ┌──────────┐
            │  Redis   │        │PostgreSQL│
            │ (Cache)  │        │(Storage) │
            └──────────┘        └──────────┘
```

### Resource Requirements

| Service | CPU | Memory | Storage |
|---------|-----|--------|---------|
| LangGraph API | 0.5-1 core | 512MB-1GB | - |
| n8n | 0.5-1 core | 512MB-1GB | 1GB |
| Redis | 0.25 core | 256MB | 1GB |
| PostgreSQL | 0.5 core | 512MB | 10GB |

## Health Checks

### LangGraph API

```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "service": "langgraph-api"}
```

### n8n

```bash
curl http://localhost:5678/healthz
# Response: {"status": "ok"}
```

### Full System Check

```bash
# Check all services
docker-compose ps

# Check logs for errors
docker-compose logs --tail=100 | grep -i error
```

## Monitoring

### Logging

**View service logs:**

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f langgraph-api

# Last 100 lines
docker-compose logs --tail=100 langgraph-api
```

### LangSmith Integration (Optional)

Enable LangChain tracing for detailed observability:

```bash
# .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_PROJECT=my-project
```

### Prometheus Metrics (Advanced)

Add to `docker-compose.yml`:

```yaml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"
```

## Scaling

### Horizontal Scaling

**Scale LangGraph API:**

```bash
docker-compose up -d --scale langgraph-api=3
```

**Add load balancer (nginx):**

```nginx
upstream langgraph {
    server langgraph-api-1:8000;
    server langgraph-api-2:8000;
    server langgraph-api-3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://langgraph;
    }
}
```

### Redis Cluster (High Availability)

For production, consider Redis Cluster or managed Redis:

```yaml
# docker-compose.override.yml
services:
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --cluster-enabled yes
```

## Security

### API Security

1. **Enable Authentication:**
   ```python
   # Add to integration/api/server.py
   from fastapi.security import APIKeyHeader
   
   api_key_header = APIKeyHeader(name="X-API-Key")
   ```

2. **Rate Limiting:**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   ```

### Network Security

1. **Use Internal Networks:**
   ```yaml
   networks:
     internal:
       internal: true
     external:
       internal: false
   ```

2. **TLS/SSL:**
   - Use reverse proxy (nginx) with SSL certificates
   - Let's Encrypt for free certificates

### Secrets Management

1. **Docker Secrets:**
   ```yaml
   secrets:
     openai_key:
       external: true
   ```

2. **Environment Variables:**
   - Never commit `.env` to version control
   - Use secrets management in production (Vault, AWS Secrets Manager)

## Backup & Recovery

### Database Backup

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U n8n n8n > backup.sql

# Restore
cat backup.sql | docker-compose exec -T postgres psql -U n8n n8n
```

### Redis Backup

```bash
# Trigger RDB snapshot
docker-compose exec redis redis-cli BGSAVE

# Copy dump file
docker cp redis:/data/dump.rdb ./backup/
```

## Troubleshooting

### Common Issues

1. **Container Won't Start:**
   ```bash
   docker-compose logs langgraph-api
   # Check for missing environment variables or dependencies
   ```

2. **Connection Refused:**
   ```bash
   # Check if service is running
   docker-compose ps
   # Check network connectivity
   docker network ls
   ```

3. **Out of Memory:**
   ```bash
   # Check memory usage
   docker stats
   # Increase limits in docker-compose.yml
   ```

4. **API Timeout:**
   - Increase timeout in n8n HTTP Request nodes
   - Check OpenAI API rate limits
   - Scale LangGraph API horizontally

### Debug Mode

```bash
# Run with debug logging
docker-compose up langgraph-api
# Check output for detailed logs
```

## Upgrading

### Update Services

```bash
# Pull latest images
docker-compose pull

# Rebuild custom images
docker-compose build --no-cache

# Restart with new images
docker-compose up -d
```

### Database Migrations

```bash
# Backup before upgrade
docker-compose exec postgres pg_dump -U n8n n8n > pre-upgrade.sql

# Apply migrations (if any)
# Check release notes for migration instructions
```
