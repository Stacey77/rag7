# Production Deployment Guide

## Overview

This guide covers deploying the Ragamuffin platform to production environments with security, scalability, and reliability best practices.

## Prerequisites

- Docker and Docker Compose (or Kubernetes)
- Domain name with DNS configuration
- SSL/TLS certificates
- Cloud provider account (AWS, GCP, Azure, or on-premise)
- Database server (PostgreSQL recommended)
- Redis server (for rate limiting and caching)
- Object storage (S3-compatible)
- Monitoring infrastructure (Prometheus, Grafana)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer (HTTPS)                    │
│                    (AWS ALB, Nginx, Traefik)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌──────────────────┐          ┌──────────────────┐
│   Frontend       │          │   Backend API    │
│   (React App)    │          │   (FastAPI)      │
│   - Nginx        │          │   - Auth/RBAC    │
│   - Static       │          │   - Rate Limit   │
└──────────────────┘          └────────┬─────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
            ┌───────────────┐  ┌──────────────┐  ┌──────────────┐
            │  RAG Service  │  │   Milvus     │  │   n8n        │
            │  (FastAPI)    │  │  (Vector DB) │  │ (Workflows)  │
            └───────────────┘  └──────────────┘  └──────────────┘
                    │                  │
                    └──────────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
            ┌──────────────┐  ┌──────────────┐
            │   MinIO      │  │     Etcd     │
            │  (S3 Store)  │  │  (Metadata)  │
            └──────────────┘  └──────────────┘
```

## Step-by-Step Deployment

### 1. Infrastructure Setup

#### Option A: Docker Compose (Simple Deployment)

**1.1. Prepare Server**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**1.2. Configure Environment**
```bash
# Clone repository
git clone https://github.com/Stacey77/rag7.git
cd rag7

# Create production .env file
cp .env.example .env.production

# Edit with production values
nano .env.production
```

**1.3. Production Environment Variables**
```bash
# .env.production

# Application
NODE_ENV=production
PYTHON_ENV=production

# Security
JWT_SECRET_KEY=<generated-with-openssl-rand-hex-32>
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Database (replace with real PostgreSQL)
DATABASE_URL=postgresql://user:password@db-host:5432/ragamuffin
REDIS_URL=redis://redis-host:6379/0

# Services
BACKEND_URL=https://api.yourdomain.com
RAG_SERVICE_URL=https://rag-api.yourdomain.com
LANGFLOW_URL=https://langflow.yourdomain.com
N8N_URL=https://n8n.yourdomain.com

# Milvus
MILVUS_HOST=milvus
MILVUS_PORT=19530

# MinIO (Change these!)
MINIO_ROOT_USER=<strong-random-username>
MINIO_ROOT_PASSWORD=<strong-random-password>

# n8n (Change these!)
N8N_BASIC_AUTH_USER=<admin-username>
N8N_BASIC_AUTH_PASSWORD=<strong-password>

# OpenAI (optional)
OPENAI_API_KEY=sk-...

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=<app-password>
```

#### Option B: Kubernetes (Scalable Deployment)

**1.1. Kubernetes Cluster**
```bash
# Create cluster (example with AWS EKS)
eksctl create cluster --name ragamuffin-prod --region us-east-1 --nodes 3 --node-type t3.large

# Or use GKE
gcloud container clusters create ragamuffin-prod --num-nodes=3 --machine-type=n1-standard-2

# Or Azure AKS
az aks create --resource-group ragamuffin --name ragamuffin-prod --node-count 3
```

**1.2. Install Helm**
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

**1.3. Deploy with Helm Charts**
```bash
# Add necessary Helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add milvus https://milvus-io.github.io/milvus-helm/
helm repo update

# Install Milvus
helm install milvus milvus/milvus --namespace ragamuffin --create-namespace

# Install Redis
helm install redis bitnami/redis --namespace ragamuffin

# Install PostgreSQL
helm install postgresql bitnami/postgresql --namespace ragamuffin
```

### 2. SSL/TLS Setup

**2.1. Obtain Certificates**
```bash
# Using Let's Encrypt with Certbot
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com -d rag-api.yourdomain.com
```

**2.2. Configure Nginx (Reverse Proxy)**
```nginx
# /etc/nginx/sites-available/ragamuffin

# Frontend
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Backend API
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### 3. Database Setup

**3.1. PostgreSQL**
```bash
# Create database
psql -h your-db-host -U postgres
CREATE DATABASE ragamuffin;
CREATE USER ragamuffin_user WITH ENCRYPTED PASSWORD 'strong-password';
GRANT ALL PRIVILEGES ON DATABASE ragamuffin TO ragamuffin_user;

# Run migrations (create tables)
# Add migration scripts for users, flows, etc.
```

**3.2. Redis**
```bash
# Configure Redis for rate limiting and caching
redis-cli
CONFIG SET requirepass "strong-redis-password"
CONFIG SET maxmemory 256mb
CONFIG SET maxmemory-policy allkeys-lru
```

### 4. Deploy Application

**4.1. Build Docker Images**
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Or push to registry
docker tag ragamuffin-frontend:latest your-registry/ragamuffin-frontend:v1.0.0
docker push your-registry/ragamuffin-frontend:v1.0.0
```

**4.2. Start Services**
```bash
# Using Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 5. Monitoring Setup

**5.1. Prometheus**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
  
  - job_name: 'rag-service'
    static_configs:
      - targets: ['rag-service:8001']
  
  - job_name: 'milvus'
    static_configs:
      - targets: ['milvus:9091']
```

**5.2. Grafana Dashboards**
```bash
# Import dashboards for:
- API request rates and latencies
- Error rates (4xx, 5xx)
- RAG query performance
- Milvus collection sizes
- System resources (CPU, memory, disk)
```

### 6. Backup Strategy

**6.1. Database Backups**
```bash
# Automated PostgreSQL backups
#!/bin/bash
# /opt/scripts/backup-db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups/postgresql
pg_dump -h db-host -U ragamuffin_user ragamuffin | gzip > $BACKUP_DIR/ragamuffin_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# Upload to S3
aws s3 cp $BACKUP_DIR/ragamuffin_$DATE.sql.gz s3://your-backup-bucket/postgresql/
```

**6.2. Milvus Backups**
```bash
# Backup Milvus data
docker exec milvus-standalone tar -czf /tmp/milvus-backup.tar.gz /var/lib/milvus
docker cp milvus-standalone:/tmp/milvus-backup.tar.gz ./backups/milvus/
```

**6.3. Cron Jobs**
```cron
# /etc/crontab

# Database backup daily at 2 AM
0 2 * * * /opt/scripts/backup-db.sh

# Milvus backup weekly on Sunday at 3 AM
0 3 * * 0 /opt/scripts/backup-milvus.sh

# Log rotation
0 0 * * * /opt/scripts/rotate-logs.sh
```

### 7. Security Hardening

**7.1. Firewall Rules**
```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP (redirects to HTTPS)
sudo ufw allow 443/tcp  # HTTPS
sudo ufw deny 8000/tcp  # Block direct backend access
sudo ufw deny 8001/tcp  # Block direct RAG service access
sudo ufw enable
```

**7.2. Fail2Ban**
```bash
# Install Fail2Ban
sudo apt install fail2ban

# Configure for API protection
# /etc/fail2ban/jail.local
[nginx-rate-limit]
enabled = true
filter = nginx-rate-limit
logpath = /var/log/nginx/error.log
maxretry = 5
findtime = 600
bantime = 3600
```

### 8. CI/CD Pipeline

**8.1. GitHub Actions Example**
```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run tests
        run: |
          docker-compose -f docker-compose.test.yml up --abort-on-container-exit
      
      - name: Build images
        run: |
          docker-compose -f docker-compose.prod.yml build
      
      - name: Push to registry
        run: |
          docker login -u ${{ secrets.DOCKER_USER }} -p ${{ secrets.DOCKER_PASSWORD }}
          docker-compose -f docker-compose.prod.yml push
      
      - name: Deploy to production
        run: |
          ssh user@production-server "cd /opt/ragamuffin && docker-compose pull && docker-compose up -d"
```

### 9. Health Checks

**9.1. Implement Health Endpoints**
```python
# Add to backend
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "database": await check_database(),
            "milvus": await check_milvus(),
            "rag_service": await check_rag_service()
        }
    }
```

**9.2. Monitor with Uptime Robot or Similar**
```
- Check /health endpoint every 5 minutes
- Alert on failures via email/SMS/Slack
- Monitor from multiple regions
```

### 10. Scaling Considerations

**10.1. Horizontal Scaling**
```yaml
# docker-compose.prod.yml (with scaling)
services:
  backend:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 2G
  
  rag-service:
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

**10.2. Load Balancing**
```
- Use AWS ALB, GCP Load Balancer, or Nginx
- Enable session affinity if needed
- Configure health checks
- Set up auto-scaling based on metrics
```

## Troubleshooting

### Common Issues

**1. Out of Memory**
```bash
# Check memory usage
docker stats

# Increase limits in docker-compose
resources:
  limits:
    memory: 4G
```

**2. Database Connection Issues**
```bash
# Test connection
psql -h db-host -U user -d database

# Check firewall
telnet db-host 5432
```

**3. SSL Certificate Renewal**
```bash
# Test renewal
sudo certbot renew --dry-run

# Auto-renew cron job
0 0 1 * * certbot renew --quiet
```

## Maintenance

### Regular Tasks

- **Daily:** Check logs for errors
- **Weekly:** Review security alerts, update dependencies
- **Monthly:** Test backups, review performance metrics
- **Quarterly:** Security audit, rotate secrets
- **Annually:** Penetration testing, disaster recovery drill

## Support

For production support:
- Documentation: https://docs.yourdomain.com
- Status page: https://status.yourdomain.com
- Support email: support@yourdomain.com
- Emergency hotline: +1-XXX-XXX-XXXX

## Compliance

Ensure compliance with:
- GDPR (EU users)
- CCPA (California users)
- HIPAA (healthcare data)
- SOC 2 (enterprise customers)
- ISO 27001 (security certification)
