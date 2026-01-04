# Ragamuffin Production Deployment Guide

This guide covers deploying Ragamuffin to production environments.

## Prerequisites

- Docker and Docker Compose installed
- Domain name configured with DNS
- SSL/TLS certificates (Let's Encrypt recommended)
- Firewall configured
- Minimum 4GB RAM, 2 CPU cores recommended

## Quick Production Deployment

### 1. Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.production.example .env.production
```

Edit `.env.production` and set the following **required** variables:

```bash
# Your domain
ALLOWED_ORIGINS=https://yourdomain.com
VITE_API_URL=https://api.yourdomain.com

# Generate secure keys (CRITICAL)
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

# Optional: Database for persistent storage
DATABASE_URL=postgresql://user:password@localhost:5432/ragamuffin
```

### 2. SSL/TLS Setup

#### Option A: Using Nginx Reverse Proxy (Recommended)

Create `nginx/nginx.conf`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Frontend
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # LangFlow (optional - restrict access)
    location /langflow/ {
        proxy_pass http://langflow:7860/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Restrict to specific IPs
        # allow 1.2.3.4;
        # deny all;
    }
}
```

#### Option B: Using Traefik (Alternative)

Add labels to `docker-compose.prod.yml` services for automatic SSL with Let's Encrypt.

### 3. Deploy

```bash
# Build and start services
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# Check logs
docker compose -f docker-compose.prod.yml logs -f

# Check health
docker compose -f docker-compose.prod.yml ps
```

### 4. Verify Deployment

```bash
# Check backend health
curl https://api.yourdomain.com/

# Check frontend
curl https://yourdomain.com/

# Expected response: HTTP 200 with content
```

## Security Checklist

Before going live, ensure you've completed:

### Critical Security Items

- [ ] Changed default `SECRET_KEY` and `JWT_SECRET` to strong random values
- [ ] Configured `ALLOWED_ORIGINS` to only your domain(s)
- [ ] Enabled authentication (`ENABLE_AUTH=true`)
- [ ] Set up SSL/TLS certificates (HTTPS only)
- [ ] Configured firewall to only allow ports 80 and 443
- [ ] Removed or secured LangFlow UI (port 7860)
- [ ] Set up database for persistent storage (not filesystem)
- [ ] Configured backup strategy

### Recommended Security Items

- [ ] Implement rate limiting at nginx/reverse proxy level
- [ ] Set up monitoring and alerting
- [ ] Enable audit logging
- [ ] Configure log rotation
- [ ] Set up intrusion detection (fail2ban)
- [ ] Implement Web Application Firewall (WAF)
- [ ] Regular security updates and patches
- [ ] Vulnerability scanning
- [ ] Penetration testing

## Authentication Setup

The backend supports JWT-based authentication. To enable:

1. Set `ENABLE_AUTH=true` in `.env.production`
2. Set strong `JWT_SECRET`
3. Implement user registration/login (see backend README)

Example login endpoint to add to `app/main.py`:

```python
from datetime import datetime, timedelta
from jose import jwt

@app.post("/auth/login")
async def login(username: str, password: str):
    # Validate credentials (implement your logic)
    # Generate JWT token
    token_data = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(token_data, JWT_SECRET, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}
```

## Database Setup

### PostgreSQL (Recommended)

1. Install PostgreSQL:
```bash
docker run -d \
  --name ragamuffin-db \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=ragamuffin \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:15-alpine
```

2. Update `.env.production`:
```bash
DATABASE_URL=postgresql://postgres:yourpassword@ragamuffin-db:5432/ragamuffin
```

3. Run migrations (implement in backend)

### MongoDB (Alternative)

For document-based storage:

```bash
docker run -d \
  --name ragamuffin-mongodb \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=yourpassword \
  -v mongodb-data:/data/db \
  mongo:7
```

## Monitoring and Logging

### Application Logs

```bash
# View all logs
docker compose -f docker-compose.prod.yml logs -f

# View specific service
docker compose -f docker-compose.prod.yml logs -f backend

# Export logs
docker compose -f docker-compose.prod.yml logs > ragamuffin-logs.txt
```

### Metrics and Monitoring

Consider integrating:

- **Prometheus + Grafana**: Metrics and dashboards
- **ELK Stack**: Centralized logging
- **Sentry**: Error tracking
- **Uptime monitors**: StatusCake, Pingdom, UptimeRobot

## Backup and Recovery

### Backup Flows

```bash
# Backup flows directory
docker compose -f docker-compose.prod.yml exec backend tar czf /tmp/flows-backup.tar.gz /app/flows

# Copy to host
docker compose -f docker-compose.prod.yml cp backend:/tmp/flows-backup.tar.gz ./backups/
```

### Backup Database

```bash
# PostgreSQL
docker exec ragamuffin-db pg_dump -U postgres ragamuffin > backup.sql

# MongoDB
docker exec ragamuffin-mongodb mongodump --out /tmp/backup
```

## Scaling

### Horizontal Scaling

1. Use a load balancer (nginx, HAProxy)
2. Scale backend service:
```bash
docker compose -f docker-compose.prod.yml up -d --scale backend=3
```
3. Use Redis for session storage
4. Use external database (managed PostgreSQL/MongoDB)

### Vertical Scaling

Adjust resource limits in `docker-compose.prod.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## Troubleshooting

### Service Not Starting

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs backend

# Check container status
docker compose -f docker-compose.prod.yml ps

# Rebuild specific service
docker compose -f docker-compose.prod.yml up -d --build backend
```

### SSL Certificate Issues

```bash
# Test SSL configuration
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Renew Let's Encrypt certificate
certbot renew
```

### Database Connection Issues

```bash
# Test database connection
docker compose -f docker-compose.prod.yml exec backend python -c "import psycopg2; print('OK')"

# Check database logs
docker logs ragamuffin-db
```

## Maintenance

### Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.prod.yml up -d --build

# Remove old images
docker image prune -a
```

### Health Checks

All services have health checks configured. Monitor with:

```bash
docker compose -f docker-compose.prod.yml ps
```

## Cloud Deployment

### AWS

- Use ECS/EKS for container orchestration
- RDS for managed database
- S3 for flow storage
- CloudFront for CDN
- Route53 for DNS

### Google Cloud

- Use Cloud Run or GKE
- Cloud SQL for database
- Cloud Storage for flows
- Cloud CDN
- Cloud DNS

### Azure

- Use Azure Container Instances or AKS
- Azure Database for PostgreSQL
- Azure Blob Storage
- Azure CDN
- Azure DNS

## Support and Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangFlow Documentation](https://docs.langflow.org/)
- [Docker Documentation](https://docs.docker.com/)
- [Let's Encrypt](https://letsencrypt.org/)

## Emergency Procedures

### Rollback

```bash
# Stop current deployment
docker compose -f docker-compose.prod.yml down

# Checkout previous version
git checkout <previous-commit>

# Redeploy
docker compose -f docker-compose.prod.yml up -d --build
```

### Service Recovery

```bash
# Restart all services
docker compose -f docker-compose.prod.yml restart

# Restart specific service
docker compose -f docker-compose.prod.yml restart backend
```
