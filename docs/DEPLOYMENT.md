# Deployment Guide

This guide covers deployment to Cloud Run, Google Kubernetes Engine (GKE), and Vertex AI.

## Prerequisites

- Google Cloud Platform account
- `gcloud` CLI installed and configured
- Docker installed locally
- `kubectl` installed (for GKE)
- Repository cloned locally

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required variables:
- `GEMINI_API_KEY`: Google Gemini API key
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `GOOGLE_PROJECT_ID`: Your GCP project ID
- Database credentials
- Redis configuration

### Secrets Management

Use Google Secret Manager for production:

```bash
# Create secrets
gcloud secrets create gemini-api-key --data-file=- < gemini_key.txt
gcloud secrets create openai-api-key --data-file=- < openai_key.txt

# Grant access to service account
gcloud secrets add-iam-policy-binding gemini-api-key \
    --member="serviceAccount:SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## Cloud Run Deployment

### Manual Deployment

1. **Build and push container**:
```bash
export PROJECT_ID=your-project-id
export REGION=us-central1

# Build
docker build -t gcr.io/$PROJECT_ID/rag7-agent-api:latest .

# Push
docker push gcr.io/$PROJECT_ID/rag7-agent-api:latest
```

2. **Deploy to Cloud Run**:
```bash
gcloud run deploy rag7-agent-api \
    --image=gcr.io/$PROJECT_ID/rag7-agent-api:latest \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --min-instances=1 \
    --max-instances=10 \
    --cpu=2 \
    --memory=4Gi \
    --timeout=300 \
    --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=INFO"
```

### CI/CD Deployment

Use GitHub Actions workflow:

```bash
# Trigger deployment to dev
gh workflow run deploy-cloud-run.yml -f environment=dev

# Trigger canary deployment to prod
gh workflow run deploy-cloud-run.yml -f environment=prod -f traffic_percentage=10
```

### Progressive Rollout

1. Deploy new revision with 10% traffic:
```bash
gh workflow run deploy-cloud-run.yml -f environment=prod -f traffic_percentage=10
```

2. Monitor metrics (error rate, latency)

3. Increase to 50%:
```bash
gcloud run services update-traffic rag7-agent-api-prod \
    --to-revisions=REVISION=50 \
    --region=$REGION
```

4. Complete rollout:
```bash
gcloud run services update-traffic rag7-agent-api-prod \
    --to-latest \
    --region=$REGION
```

### Rollback

```bash
# List revisions
gcloud run revisions list --service=rag7-agent-api-prod --region=$REGION

# Route all traffic to previous revision
gcloud run services update-traffic rag7-agent-api-prod \
    --to-revisions=PREVIOUS_REVISION=100 \
    --region=$REGION
```

## GKE Deployment

### Cluster Setup

1. **Create GKE cluster**:
```bash
gcloud container clusters create rag7-cluster \
    --region=$REGION \
    --num-nodes=3 \
    --machine-type=n1-standard-4 \
    --enable-autoscaling \
    --min-nodes=3 \
    --max-nodes=10 \
    --enable-stackdriver-kubernetes \
    --addons=HorizontalPodAutoscaling,HttpLoadBalancing
```

2. **Get credentials**:
```bash
gcloud container clusters get-credentials rag7-cluster --region=$REGION
```

### Deploy with Kustomize

1. **Development environment**:
```bash
kubectl apply -k deploy/gke/overlays/dev
```

2. **Staging environment**:
```bash
kubectl apply -k deploy/gke/overlays/staging
```

3. **Production environment**:
```bash
kubectl apply -k deploy/gke/overlays/prod
```

### Verify Deployment

```bash
# Check pods
kubectl get pods -n rag7-prod

# Check services
kubectl get svc -n rag7-prod

# Check ingress
kubectl get ingress -n rag7-prod

# View logs
kubectl logs -f deployment/rag7-agent-api -n rag7-prod
```

### Blue/Green Deployment

1. Deploy new version (green):
```bash
kubectl apply -f deploy/gke/blue-green/green-deployment.yaml
```

2. Test green deployment:
```bash
kubectl port-forward svc/rag7-agent-api-green 8080:80 -n rag7-prod
```

3. Switch traffic:
```bash
kubectl patch svc rag7-agent-api -n rag7-prod \
    -p '{"spec":{"selector":{"version":"green"}}}'
```

4. Clean up blue deployment:
```bash
kubectl delete deployment rag7-agent-api-blue -n rag7-prod
```

### Rollback

```bash
# Rollback deployment
kubectl rollout undo deployment/rag7-agent-api -n rag7-prod

# Rollback to specific revision
kubectl rollout undo deployment/rag7-agent-api --to-revision=2 -n rag7-prod
```

## Vertex AI Deployment

### Setup

1. **Navigate to Vertex AI directory**:
```bash
cd deploy/vertex-ai
```

2. **Configure agent**:
Edit `agent-config.yaml` with your settings.

3. **Deploy**:
```bash
./deploy.sh dev
```

### Environment-Specific Deployment

```bash
# Development
./deploy.sh dev

# Staging
./deploy.sh staging

# Production (requires manual approval)
./deploy.sh prod
```

## Monitoring Deployment

### Health Checks

```bash
# Cloud Run
curl https://rag7-agent-api-SERVICE.run.app/health

# GKE
kubectl exec -it POD_NAME -n rag7-prod -- curl localhost:8080/health
```

### Metrics

Access Prometheus:
```bash
# Port forward
kubectl port-forward svc/prometheus 9090:9090 -n monitoring
```

Access Grafana:
```bash
# Port forward
kubectl port-forward svc/grafana 3000:3000 -n monitoring
```

### Logs

Cloud Run:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=rag7-agent-api" \
    --limit=50 \
    --format=json
```

GKE:
```bash
kubectl logs -f deployment/rag7-agent-api -n rag7-prod
```

## Troubleshooting

### Common Issues

**Issue**: Pod CrashLoopBackOff
```bash
# Check logs
kubectl logs POD_NAME -n rag7-prod --previous

# Describe pod
kubectl describe pod POD_NAME -n rag7-prod
```

**Issue**: Service not accessible
```bash
# Check service endpoints
kubectl get endpoints -n rag7-prod

# Check ingress
kubectl describe ingress rag7-agent-api-ingress -n rag7-prod
```

**Issue**: High latency
```bash
# Check HPA status
kubectl get hpa -n rag7-prod

# Scale manually if needed
kubectl scale deployment rag7-agent-api --replicas=10 -n rag7-prod
```

## Maintenance

### Update Dependencies

```bash
# Update Docker image
docker pull python:3.11-slim

# Rebuild
make docker-build

# Deploy
kubectl set image deployment/rag7-agent-api \
    agent-api=gcr.io/$PROJECT_ID/rag7-agent-api:NEW_TAG \
    -n rag7-prod
```

### Database Migrations

```bash
# Run migrations
kubectl exec -it deployment/rag7-agent-api -n rag7-prod -- \
    python -m alembic upgrade head
```

### Backup

```bash
# Backup PostgreSQL
kubectl exec -it postgres-0 -n rag7-prod -- \
    pg_dump -U rag7_user rag7_db > backup.sql

# Backup Redis
kubectl exec -it redis-0 -n rag7-prod -- \
    redis-cli SAVE
```

## Cost Optimization

### Auto-scaling Configuration

Adjust based on load:
```yaml
spec:
  minReplicas: 1  # Reduce for dev/staging
  maxReplicas: 50 # Increase for prod
```

### Resource Limits

Right-size containers:
```yaml
resources:
  requests:
    memory: "2Gi"   # Adjust based on actual usage
    cpu: "1000m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

---

For architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md).
For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
