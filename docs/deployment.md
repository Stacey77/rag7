# Deployment Guide

This guide covers deploying the Rag7 application using Docker Compose or Kubernetes.

## Prerequisites

- Docker and Docker Compose (for Docker Compose deployment)
- kubectl and access to a Kubernetes cluster (for K8s deployment)
- GitHub Container Registry (GHCR) access token
- Production environment variables configured

## Docker Compose Deployment

### 1. Prepare Environment

Copy the example environment file and configure it:

```bash
cp .env.prod.example .env.prod
```

Edit `.env.prod` and fill in all required values:
- Database credentials
- Redis password
- API keys (OpenAI, LangGraph)
- n8n encryption key
- Secret keys

### 2. Pull Docker Images

Login to GitHub Container Registry:

```bash
echo $GHCR_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

Pull the latest image:

```bash
docker pull ghcr.io/stacey77/rag7:latest
```

### 3. Start Services

Start all services:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Verify Deployment

Check service health:

```bash
# Check all services are running
docker-compose -f docker-compose.prod.yml ps

# Check LangGraph API health
curl http://localhost:8000/health

# Check n8n is accessible
curl http://localhost:5678
```

### 5. Import n8n Workflows

1. Access n8n at `http://localhost:5678`
2. Complete initial setup
3. Import workflows from `n8n/workflows/` directory
4. Configure credentials using templates in `n8n/credentials/`

### Stopping Services

```bash
docker-compose -f docker-compose.prod.yml down
```

To remove volumes (⚠️ deletes data):

```bash
docker-compose -f docker-compose.prod.yml down -v
```

---

## Kubernetes Deployment

### 1. Prepare Cluster

Ensure you have:
- A running Kubernetes cluster (v1.24+)
- kubectl configured to access the cluster
- Namespace created: `kubectl create namespace rag7-staging`

### 2. Create Secrets

⚠️ **IMPORTANT**: These secrets MUST be created before deploying the application. The deployment will fail if these secrets don't exist.

Create the application secrets:

```bash
kubectl create secret generic langgraph-secrets \
  --from-literal=postgres-host=YOUR_POSTGRES_HOST \
  --from-literal=postgres-db=rag7_prod \
  --from-literal=postgres-user=rag7user \
  --from-literal=postgres-password=YOUR_POSTGRES_PASSWORD \
  --from-literal=redis-host=YOUR_REDIS_HOST \
  --from-literal=redis-password=YOUR_REDIS_PASSWORD \
  --from-literal=openai-api-key=YOUR_OPENAI_API_KEY \
  --from-literal=secret-key=YOUR_SECRET_KEY \
  -n rag7-staging
```

Verify the secret was created:

```bash
kubectl get secret langgraph-secrets -n rag7-staging
```

Create Docker registry secret for pulling images:

```bash
kubectl create secret docker-registry ghcr-pull-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_TOKEN \
  -n rag7-staging
```

Verify the secret was created:

```bash
kubectl get secret ghcr-pull-secret -n rag7-staging
```

### 3. Deploy Application

Apply the Kubernetes manifests:

```bash
# Deploy the application
kubectl apply -f k8s/langgraph-deployment.yaml

# Enable auto-scaling
kubectl apply -f k8s/hpa.yaml
```

### 4. Verify Deployment

Check deployment status:

```bash
# Check pods are running
kubectl get pods -n rag7-staging -l app=langgraph-api

# Check service
kubectl get svc -n rag7-staging langgraph-api

# View logs
kubectl logs -n rag7-staging -l app=langgraph-api --tail=50 -f

# Check HPA status
kubectl get hpa -n rag7-staging
```

### 5. Access the Application

Get the service endpoint:

```bash
# For LoadBalancer service
kubectl get svc langgraph-api -n rag7-staging -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Port-forward for local testing
kubectl port-forward -n rag7-staging svc/langgraph-api 8000:80
```

Test the endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Readiness check
curl http://localhost:8000/ready

# Test graph endpoint
curl -X POST http://localhost:8000/v1/graph/run \
  -H "Content-Type: application/json" \
  -d '{"input": "test query"}'
```

### 6. Rollback (if needed)

View deployment history:

```bash
kubectl rollout history deployment/langgraph-api -n rag7-staging
```

Rollback to previous version:

```bash
kubectl rollout undo deployment/langgraph-api -n rag7-staging
```

---

## Database Setup

For production deployments, consider using managed database services:

### PostgreSQL

- AWS RDS for PostgreSQL
- Google Cloud SQL
- Azure Database for PostgreSQL
- DigitalOcean Managed Databases

Update the connection details in secrets accordingly.

### Redis

- AWS ElastiCache
- Google Cloud Memorystore
- Azure Cache for Redis
- DigitalOcean Managed Redis

---

## SSL/TLS Configuration

### Docker Compose

Use a reverse proxy like nginx or Traefik:

```bash
# Example with Traefik labels in docker-compose.prod.yml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.langgraph.rule=Host(`api.example.com`)"
  - "traefik.http.routers.langgraph.tls=true"
  - "traefik.http.routers.langgraph.tls.certresolver=letsencrypt"
```

### Kubernetes

Create an Ingress resource:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: langgraph-ingress
  namespace: rag7-staging
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.example.com
    secretName: langgraph-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: langgraph-api
            port:
              number: 80
```

---

## Troubleshooting

### Logs

Docker Compose:
```bash
docker-compose -f docker-compose.prod.yml logs -f langgraph
```

Kubernetes:
```bash
kubectl logs -n rag7-staging -l app=langgraph-api --tail=100 -f
```

### Common Issues

1. **Container fails to start**: Check environment variables and secrets
2. **Database connection errors**: Verify database credentials and network connectivity
3. **Health checks failing**: Increase `initialDelaySeconds` if application needs more startup time
4. **Image pull errors**: Verify GHCR token has `packages:read` scope

For more troubleshooting steps, see [runbook.md](./runbook.md).
