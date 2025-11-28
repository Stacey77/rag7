# Ragamuffin Platform - Deployment Checklist

## Overview

Use this checklist before deploying to staging or production environments. Complete all items to ensure a secure and reliable deployment.

## Pre-Deployment Checklist

### 1. Environment Setup ✅

- [ ] **Clone repository**
  ```bash
  git clone https://github.com/Stacey77/rag7.git
  cd rag7
  ```

- [ ] **Copy environment template**
  ```bash
  # For staging
  cp .env.staging.example .env.staging
  
  # For production
  cp .env.example .env.production
  ```

- [ ] **Generate secure secrets**
  ```bash
  # Generate JWT secret
  openssl rand -hex 32
  
  # Generate n8n encryption key
  openssl rand -hex 32
  
  # Generate strong passwords
  openssl rand -base64 24
  ```

### 2. Security Configuration ✅

- [ ] **JWT Authentication**
  - [ ] Set unique `JWT_SECRET_KEY` (32+ hex characters)
  - [ ] Configure appropriate `ACCESS_TOKEN_EXPIRE_MINUTES`
  - [ ] Set `REFRESH_TOKEN_EXPIRE_DAYS`

- [ ] **Service Credentials** (Change ALL defaults!)
  - [ ] `N8N_BASIC_AUTH_USER` - Custom admin username
  - [ ] `N8N_BASIC_AUTH_PASSWORD` - Strong password (16+ chars)
  - [ ] `MINIO_ROOT_USER` - Custom admin username
  - [ ] `MINIO_ROOT_PASSWORD` - Strong password (16+ chars)
  - [ ] `N8N_ENCRYPTION_KEY` - 32 hex characters

- [ ] **CORS Configuration**
  - [ ] Set `CORS_ORIGINS` to your actual domains
  - [ ] Remove localhost entries for production

- [ ] **Rate Limiting**
  - [ ] Configure `RATE_LIMIT_PER_MINUTE` appropriately

### 3. Infrastructure Requirements ✅

- [ ] **System Resources**
  - [ ] Minimum 8GB RAM (16GB recommended)
  - [ ] Minimum 20GB disk space (50GB recommended)
  - [ ] 4+ CPU cores recommended

- [ ] **Docker**
  - [ ] Docker Engine 20.10+
  - [ ] Docker Compose 2.0+

- [ ] **Network Ports Available**
  | Service | Port | Required |
  |---------|------|----------|
  | Frontend | 8080 | Yes |
  | Backend API | 8000 | Yes |
  | RAG Service | 8001 | Yes |
  | LangFlow | 7860 | Yes |
  | n8n | 5678 | Yes |
  | MinIO | 9000, 9001 | Yes |
  | Milvus | 19530 | Yes |

### 4. DNS & SSL (Production) ✅

- [ ] **Domain Configuration**
  - [ ] Point domain to server IP
  - [ ] Configure subdomains (api, rag-api, n8n, etc.)

- [ ] **SSL/TLS Certificates**
  - [ ] Obtain certificates (Let's Encrypt recommended)
  - [ ] Configure reverse proxy (Nginx)
  - [ ] Enable HTTPS redirect

### 5. Database Setup (Optional) ✅

For production, replace in-memory storage:

- [ ] **PostgreSQL**
  ```bash
  # Create database
  CREATE DATABASE ragamuffin;
  CREATE USER ragamuffin_user WITH ENCRYPTED PASSWORD 'strong-password';
  GRANT ALL PRIVILEGES ON DATABASE ragamuffin TO ragamuffin_user;
  ```

- [ ] **Redis** (for caching/rate limiting)
  ```bash
  # Configure password
  redis-cli CONFIG SET requirepass "strong-password"
  ```

### 6. Monitoring Setup ✅

- [ ] **Health Endpoints**
  - [ ] Verify `/health` endpoint on all services
  - [ ] Set up uptime monitoring (UptimeRobot, Pingdom)

- [ ] **Logging**
  - [ ] Configure log aggregation
  - [ ] Set appropriate log levels

- [ ] **Alerting**
  - [ ] Configure alerts for service failures
  - [ ] Set up email/Slack notifications

### 7. Backup Configuration ✅

- [ ] **Database Backups**
  - [ ] Schedule daily PostgreSQL backups
  - [ ] Configure backup retention (30 days minimum)

- [ ] **Milvus Backups**
  - [ ] Schedule weekly vector database backups
  - [ ] Test backup restoration

- [ ] **Flow Files**
  - [ ] Back up `langflow-backend/flows/` directory

---

## Deployment Steps

### Staging Deployment

```bash
# 1. Run checklist
./deploy-staging.sh --checklist

# 2. Deploy
./deploy-staging.sh --build

# 3. Verify services
./deploy-staging.sh --status

# 4. Check logs for errors
./deploy-staging.sh --logs
```

### Production Deployment

```bash
# 1. Build images
docker-compose -f docker-compose.prod.yml build

# 2. Deploy
docker-compose -f docker-compose.prod.yml up -d

# 3. Verify health
curl -f http://localhost:8000/health
curl -f http://localhost:8001/health

# 4. Check all services
docker-compose -f docker-compose.prod.yml ps
```

---

## Post-Deployment Verification

### 1. Service Health Checks ✅

- [ ] Frontend loads at configured URL
- [ ] Backend API docs accessible (`/docs`)
- [ ] RAG service health check passes
- [ ] LangFlow UI accessible
- [ ] n8n login works with configured credentials
- [ ] MinIO console accessible

### 2. Functional Tests ✅

- [ ] **Flow Management**
  ```bash
  # Create test flow
  echo '{"nodes": [], "edges": []}' > test.json
  curl -X POST -F "flow_file=@test.json" http://localhost:8000/save_flow/
  curl http://localhost:8000/list_flows/
  ```

- [ ] **RAG Operations**
  ```bash
  # Test embedding
  curl -X POST "http://localhost:8000/rag/embed" \
    -F "texts=Test document" \
    -F "collection_name=test_collection"
  
  # Test search
  curl -X POST "http://localhost:8000/rag/search" \
    -F "text=test query" -F "top_k=5"
  ```

### 3. Security Verification ✅

- [ ] CORS blocks unauthorized origins
- [ ] Rate limiting triggers on excessive requests
- [ ] JWT authentication required for protected endpoints
- [ ] Security headers present in responses

---

## Rollback Procedure

If deployment fails:

```bash
# 1. Stop new deployment
./deploy-staging.sh --stop

# 2. Restore previous version
git checkout <previous-commit>

# 3. Redeploy
./deploy-staging.sh --build

# 4. Verify restoration
./deploy-staging.sh --status
```

---

## Quick Reference

### Environment Files

| Environment | File | Compose File |
|-------------|------|--------------|
| Development | `.env` | `docker-compose.yml` |
| Staging | `.env.staging` | `docker-compose.staging.yml` |
| Production | `.env.production` | `docker-compose.prod.yml` |

### Common Commands

```bash
# Start staging
./deploy-staging.sh

# View logs
./deploy-staging.sh --logs

# Stop services
./deploy-staging.sh --stop

# Clean restart
./deploy-staging.sh --clean

# Check status
./deploy-staging.sh --status
```

### Support Resources

- Security Guidelines: [SECURITY.md](./SECURITY.md)
- Production Guide: [PRODUCTION.md](./PRODUCTION.md)
- Run Commands: [RUN_COMMANDS.md](./RUN_COMMANDS.md)

---

## Checklist Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Developer | | | |
| Security | | | |
| Operations | | | |
| Manager | | | |

**Deployment Approved:** [ ] Yes [ ] No

**Notes:**
