# Deployment Guide

## Overview

This guide covers deploying the RAG7 platform to various environments.

## Local Development

### Quick Start

```bash
# Setup
./scripts/setup.sh

# Activate virtual environment
source venv/bin/activate

# Run development server
python -m app.main
```

Access at: http://localhost:8000

## Docker Deployment

### Single Container

```bash
# Build
docker build -t rag7:latest .

# Run
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name rag7-api \
  rag7:latest
```

### Docker Compose (Recommended)

Full stack with Redis, PostgreSQL, and ChromaDB:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services:
- API: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- ChromaDB: http://localhost:8001

## Production Deployment

### Prerequisites

- Domain name
- SSL/TLS certificates
- Load balancer
- Monitoring setup

### Environment Configuration

Create production `.env`:

```bash
# API Configuration
API_ENV=production
API_HOST=0.0.0.0
API_PORT=8000

# LLM Providers
OPENAI_API_KEY=sk-prod-xxxxx
ANTHROPIC_API_KEY=sk-ant-prod-xxxxx

# Vector Databases
PINECONE_API_KEY=prod-xxxxx
PINECONE_ENVIRONMENT=us-east-1-aws

# Database
DATABASE_URL=postgresql://user:pass@prod-db:5432/rag7
REDIS_URL=redis://prod-redis:6379

# Security
SECRET_KEY=use-strong-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Monitoring
ENABLE_METRICS=true
ENABLE_TRACING=true
LOG_LEVEL=INFO
```

### Docker Production Build

```bash
# Build production image
docker build -t rag7:prod .

# Tag for registry
docker tag rag7:prod registry.example.com/rag7:latest

# Push to registry
docker push registry.example.com/rag7:latest
```

### Kubernetes Deployment

Example Kubernetes manifests:

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag7-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rag7-api
  template:
    metadata:
      labels:
        app: rag7-api
    spec:
      containers:
      - name: api
        image: registry.example.com/rag7:latest
        ports:
        - containerPort: 8000
        env:
        - name: API_ENV
          value: "production"
        envFrom:
        - secretRef:
            name: rag7-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

**service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: rag7-api
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: rag7-api
```

Deploy:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### AWS ECS

```bash
# Create ECR repository
aws ecr create-repository --repository-name rag7

# Build and push
docker build -t rag7:latest .
docker tag rag7:latest YOUR_AWS_ACCOUNT.dkr.ecr.REGION.amazonaws.com/rag7:latest
docker push YOUR_AWS_ACCOUNT.dkr.ecr.REGION.amazonaws.com/rag7:latest

# Deploy using ECS task definition
aws ecs create-service --service-name rag7-api --task-definition rag7:1
```

## Scaling

### Horizontal Scaling

Add more replicas:

```bash
# Kubernetes
kubectl scale deployment rag7-api --replicas=5

# Docker Compose
docker-compose up -d --scale api=5
```

### Auto-Scaling

**Kubernetes HPA:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: rag7-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: rag7-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Monitoring

### Prometheus

Scrape metrics from `/metrics` endpoint:

```yaml
scrape_configs:
  - job_name: 'rag7'
    static_configs:
      - targets: ['localhost:8000']
```

### Grafana Dashboard

Import dashboard from `docs/grafana-dashboard.json`

### Log Aggregation

Configure log shipping:
- ELK Stack
- Splunk
- CloudWatch Logs
- Datadog

## Security

### SSL/TLS

Use reverse proxy (nginx, Traefik) for SSL termination:

```nginx
server {
    listen 443 ssl;
    server_name api.rag7.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Firewall Rules

Allow only necessary ports:
- 443 (HTTPS)
- 80 (HTTP redirect)

### Secrets Management

Use secrets management:
- Kubernetes Secrets
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault

## Backup & Recovery

### Database Backup

```bash
# PostgreSQL
pg_dump -h localhost -U rag7 rag7 > backup.sql

# Restore
psql -h localhost -U rag7 rag7 < backup.sql
```

### Vector Store Backup

Follow provider-specific backup procedures:
- Pinecone: Use backups feature
- Weaviate: Backup volumes
- ChromaDB: Backup persistent volume

## Health Checks

Endpoints:
- `/health` - Basic health check
- `/metrics` - Prometheus metrics

Monitor:
- Response time < 500ms
- Error rate < 1%
- Uptime > 99.9%

## Troubleshooting

### Common Issues

**Container won't start:**
```bash
docker logs rag7-api
```

**Database connection failed:**
- Check DATABASE_URL
- Verify network connectivity
- Check credentials

**High latency:**
- Check LLM provider status
- Review rate limits
- Scale horizontally

**Memory issues:**
- Increase container limits
- Check for memory leaks
- Review logging verbosity

## Rollback

```bash
# Kubernetes
kubectl rollout undo deployment/rag7-api

# Docker
docker-compose down
docker-compose pull
docker-compose up -d
```

## Support

For deployment issues:
1. Check logs: `docker logs` or `kubectl logs`
2. Review documentation
3. Open GitHub issue
