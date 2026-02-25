# Deployment Guide

This guide covers deploying the RAG7 LangGraph application to production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Deployment Options](#deployment-options)
  - [Docker Compose](#docker-compose)
  - [Kubernetes](#kubernetes)
- [Post-Deployment](#post-deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

- Docker & Docker Compose (v2.0+)
- kubectl (v1.28+) for Kubernetes deployments
- Access to container registry (GitHub Container Registry)
- Database: PostgreSQL 15+
- Cache: Redis 7+

### Required Secrets

Before deploying, you must configure the following secrets:

1. **Database Credentials**: PostgreSQL password
2. **Secret Keys**: Application secret key and API key salt
3. **API Keys**: OpenAI, Anthropic, or other LLM provider keys
4. **Registry Access**: GitHub Container Registry token (for pulling images)
5. **Kubeconfig**: Kubernetes cluster credentials (for K8s deployments)

## Environment Configuration

### Step 1: Create Production Environment File

```bash
cp .env.prod.example .env.prod
```

### Step 2: Update Required Values

Edit `.env.prod` and replace all `CHANGEME_*` placeholders:

```bash
# Generate secure secret key
openssl rand -hex 32

# Generate API key salt
openssl rand -hex 16

# Generate secure database password
openssl rand -base64 32
```

### Step 3: Configure API Keys

Add your LLM provider API keys:

```bash
OPENAI_API_KEY=sk-your-actual-key-here
LANGCHAIN_API_KEY=ls__your-actual-key-here
```

## Deployment Options

### Docker Compose

Docker Compose is suitable for single-server deployments or staging environments.

#### Deploy with Docker Compose

```bash
# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f langgraph
```

#### Verify Deployment

```bash
# Check health endpoint
curl http://localhost:8000/health

# Check readiness endpoint
curl http://localhost:8000/ready

# Test graph execution
curl -X POST http://localhost:8000/v1/graph/run \
  -H "Content-Type: application/json" \
  -d '{"input": {"query": "test"}}'
```

#### Stop Services

```bash
docker-compose -f docker-compose.prod.yml down
```

### Kubernetes

Kubernetes is recommended for production deployments requiring high availability and auto-scaling.

#### Prerequisites

1. **Configure kubectl**

```bash
# Set up kubeconfig
export KUBECONFIG=/path/to/your/kubeconfig

# Verify connection
kubectl cluster-info
kubectl get nodes
```

2. **Create Namespace**

```bash
kubectl apply -f k8s/langgraph-deployment.yaml
# This creates the rag7 namespace
```

3. **Configure Secrets**

Update the secrets in `k8s/langgraph-deployment.yaml` or create them via kubectl:

```bash
# Create secrets from literal values
kubectl create secret generic langgraph-secrets \
  --namespace=rag7 \
  --from-literal=POSTGRES_PASSWORD='your-secure-password' \
  --from-literal=REDIS_PASSWORD='your-redis-password' \
  --from-literal=SECRET_KEY='your-secret-key' \
  --from-literal=API_KEY_SALT='your-api-salt' \
  --from-literal=OPENAI_API_KEY='sk-your-key' \
  --dry-run=client -o yaml | kubectl apply -f -
```

4. **Create Image Pull Secret** (for GHCR)

```bash
kubectl create secret docker-registry ghcr-secret \
  --namespace=rag7 \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_TOKEN \
  --docker-email=YOUR_EMAIL
```

#### Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/langgraph-deployment.yaml
kubectl apply -f k8s/hpa.yaml

# Check deployment status
kubectl get deployments -n rag7
kubectl get pods -n rag7
kubectl get services -n rag7

# Watch rollout
kubectl rollout status deployment/langgraph -n rag7
```

#### Verify Kubernetes Deployment

```bash
# Port-forward to test locally
kubectl port-forward -n rag7 svc/langgraph 8123:8123

# In another terminal, test endpoints
curl http://localhost:8123/health
curl http://localhost:8123/ready
```

#### Expose Service (Optional)

Using an Ingress controller:

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: langgraph-ingress
  namespace: rag7
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: langgraph-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: langgraph
            port:
              number: 8123
```

```bash
kubectl apply -f ingress.yaml
```

## Post-Deployment

### Database Migrations

Run any necessary database migrations:

```bash
# Docker Compose
docker-compose -f docker-compose.prod.yml exec langgraph python -m alembic upgrade head

# Kubernetes
kubectl exec -n rag7 -it deployment/langgraph -- python -m alembic upgrade head
```

### Monitoring Setup

1. **Check Metrics Endpoint**

```bash
curl http://localhost:9090/metrics
```

2. **Configure Prometheus** (if using)

Add scraping configuration for the metrics endpoint.

3. **Set Up Alerts**

Configure alerting rules for critical metrics.

### Backup Configuration

1. **Database Backups**

```bash
# Set up automated PostgreSQL backups
kubectl create cronjob postgres-backup \
  --image=postgres:15-alpine \
  --schedule="0 2 * * *" \
  --restart=Never \
  -- pg_dump -h postgres.rag7.svc.cluster.local -U langgraph > /backup/db.sql
```

2. **Configuration Backups**

Store ConfigMaps and Secrets in version control (encrypted).

## Troubleshooting

### Common Issues

#### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n rag7

# View pod logs
kubectl logs -n rag7 deployment/langgraph --tail=100

# Describe pod for events
kubectl describe pod -n rag7 POD_NAME
```

#### Connection Issues

```bash
# Test database connectivity
kubectl run -n rag7 -it --rm debug --image=postgres:15-alpine --restart=Never \
  -- psql -h postgres.rag7.svc.cluster.local -U langgraph -d langgraph_checkpoints

# Test Redis connectivity
kubectl run -n rag7 -it --rm debug --image=redis:7-alpine --restart=Never \
  -- redis-cli -h redis.rag7.svc.cluster.local -a PASSWORD ping
```

#### Image Pull Errors

```bash
# Verify image pull secret
kubectl get secret ghcr-secret -n rag7 -o yaml

# Test image pull manually
docker pull ghcr.io/stacey77/rag7:latest
```

#### Resource Constraints

```bash
# Check resource usage
kubectl top pods -n rag7

# Check HPA status
kubectl get hpa -n rag7

# Describe HPA for details
kubectl describe hpa langgraph-hpa -n rag7
```

### Logs and Debugging

```bash
# Stream all logs
kubectl logs -n rag7 -l app=langgraph --tail=100 -f

# Get logs from specific pod
kubectl logs -n rag7 POD_NAME --tail=200

# Get previous crashed container logs
kubectl logs -n rag7 POD_NAME --previous
```

### Rollback Deployment

```bash
# View rollout history
kubectl rollout history deployment/langgraph -n rag7

# Rollback to previous version
kubectl rollout undo deployment/langgraph -n rag7

# Rollback to specific revision
kubectl rollout undo deployment/langgraph -n rag7 --to-revision=2
```

## Next Steps

- Configure observability (see [observability.md](./observability.md))
- Set up alerting and on-call rotation (see [runbook.md](./runbook.md))
- Import n8n workflows (see [../n8n/README.md](../n8n/README.md))
- Configure CI/CD pipelines
- Set up backup and disaster recovery procedures
