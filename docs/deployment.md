# Deployment Guide

## Overview

This guide covers deploying the RAG7 LangGraph integration API to production using Docker Compose or Kubernetes.

## Prerequisites

- Docker and Docker Compose (for local/VM deployment)
- kubectl and access to a Kubernetes cluster (for K8s deployment)
- GitHub Container Registry (GHCR) access token
- Domain name and SSL certificates (optional for production)

## Deployment Options

### Option 1: Docker Compose (Recommended for VMs)

1. **Prepare Environment Variables**

   ```bash
   cp .env.prod.example .env.prod
   # Edit .env.prod and fill in all TODO values
   nano .env.prod
   ```

2. **Login to GitHub Container Registry**

   ```bash
   echo $GHCR_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
   ```

3. **Pull Latest Image**

   ```bash
   docker-compose -f docker-compose.prod.yml pull
   ```

4. **Start Services**

   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

5. **Verify Deployment**

   ```bash
   # Check service health
   curl http://localhost:8000/health
   
   # Check readiness
   curl http://localhost:8000/ready
   
   # View logs
   docker-compose -f docker-compose.prod.yml logs -f langgraph-api
   ```

### Option 2: Kubernetes

1. **Setup kubectl Context**

   ```bash
   # Ensure your kubectl is configured for the target cluster
   kubectl config current-context
   ```

2. **Create Namespace and Secrets**

   ```bash
   # Apply namespace
   kubectl create namespace rag7-prod
   
   # Create image pull secret for GHCR
   kubectl create secret docker-registry ghcr-secret \
     --docker-server=ghcr.io \
     --docker-username=USERNAME \
     --docker-password=$GHCR_TOKEN \
     --namespace=rag7-prod
   
   # Update secrets in k8s/langgraph-deployment.yaml
   # Then apply:
   kubectl apply -f k8s/langgraph-deployment.yaml
   ```

3. **Setup Autoscaling**

   ```bash
   # Install metrics-server if not present
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
   
   # Apply HPA
   kubectl apply -f k8s/hpa.yaml
   ```

4. **Verify Deployment**

   ```bash
   # Check pods
   kubectl get pods -n rag7-prod
   
   # Check service
   kubectl get svc -n rag7-prod
   
   # Check HPA status
   kubectl get hpa -n rag7-prod
   
   # Port-forward to test locally
   kubectl port-forward -n rag7-prod svc/langgraph-api 8000:80
   curl http://localhost:8000/health
   ```

## CI/CD Integration

The repository includes GitHub Actions workflows for automated deployment:

- **CI Pipeline** (`.github/workflows/ci.yml`): Runs on every push/PR to main/develop
  - Linting and code quality checks
  - Security scanning with Trivy
  - Unit tests

- **CD Pipeline** (`.github/workflows/cd-staging.yml`): Deploys to staging on push to develop
  - Builds and pushes Docker image to GHCR
  - Deploys to Kubernetes staging environment

### Required GitHub Secrets

Add these secrets to your GitHub repository settings:

- `KUBE_CONFIG_STAGING`: Base64-encoded kubeconfig for staging cluster
- `KUBE_CONFIG_PROD`: Base64-encoded kubeconfig for production cluster (if separate)

```bash
# Encode kubeconfig
cat ~/.kube/config | base64 -w 0
```

## Health Checks

The API exposes two health check endpoints:

- `GET /health`: Liveness probe - returns 200 if server is running
- `GET /ready`: Readiness probe - returns 200 if server is ready to accept traffic

## Scaling

### Docker Compose

Edit `docker-compose.prod.yml` and adjust the `deploy.resources` section:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
```

### Kubernetes

Scaling is handled by the HPA (Horizontal Pod Autoscaler):

- Min replicas: 3
- Max replicas: 10
- Target CPU: 70%
- Target Memory: 80%

Manual scaling:

```bash
kubectl scale deployment langgraph-api --replicas=5 -n rag7-prod
```

## Rollback

### Docker Compose

```bash
# Pull specific version
docker pull ghcr.io/stacey77/rag7:develop-abc123

# Update docker-compose.prod.yml with specific tag
# Restart services
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes

```bash
# View deployment history
kubectl rollout history deployment/langgraph-api -n rag7-prod

# Rollback to previous version
kubectl rollout undo deployment/langgraph-api -n rag7-prod

# Rollback to specific revision
kubectl rollout undo deployment/langgraph-api --to-revision=2 -n rag7-prod
```

## Troubleshooting

### Container Won't Start

```bash
# Docker Compose
docker-compose -f docker-compose.prod.yml logs langgraph-api

# Kubernetes
kubectl logs -n rag7-prod deployment/langgraph-api
kubectl describe pod -n rag7-prod <pod-name>
```

### Database Connection Issues

```bash
# Test database connectivity
docker-compose -f docker-compose.prod.yml exec langgraph-api python -c "import psycopg2; print('OK')"
```

### Service Not Accessible

```bash
# Check if pods are running
kubectl get pods -n rag7-prod

# Check service endpoints
kubectl get endpoints -n rag7-prod

# Check ingress
kubectl get ingress -n rag7-prod
kubectl describe ingress langgraph-api -n rag7-prod
```

## Next Steps

1. Setup SSL certificates for production domain
2. Configure DNS records
3. Setup monitoring alerts (see [observability.md](observability.md))
4. Review and test disaster recovery procedures (see [runbook.md](runbook.md))
5. Configure n8n workflows (see [integrations.md](integrations.md))
