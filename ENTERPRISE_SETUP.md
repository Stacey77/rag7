# Enterprise Features Setup Guide

This guide explains how to use the new enterprise features added to the Ragamuffin platform.

## Quick Start

```bash
# Start all services including enterprise features
./start-dev.sh

# Access services:
# - API Gateway (Traefik): http://localhost (Dashboard: http://localhost:8090)
# - PostgreSQL: localhost:5432
# - RabbitMQ Management: http://localhost:15672 (guest/guest)
# - Admin Dashboard: http://localhost/admin
```

## Services Overview

### 1. Traefik API Gateway (Port 80, 443, 8090)

Unified API management and routing for all services.

**Features:**
- Automatic service discovery
- Load balancing
- SSL/TLS termination (production)
- Request tracing
- Health checks

**Access Dashboard:** http://localhost:8090

### 2. PostgreSQL Database (Port 5432)

Persistent storage for multi-tenancy and analytics.

**Connection:**
```bash
psql -h localhost -U ragamuffin -d ragamuffin
# Password: ragamuffin_secure_password
```

**Default Credentials:**
- Admin: admin@ragamuffin.ai / admin123
- Organization: Demo Organization (demo-org)
- Workspaces: Main Project, Test Environment

### 3. RabbitMQ Message Queue (Port 5672, 15672)

Async task processing for embeddings, exports, and workflows.

**Management UI:** http://localhost:15672
**Credentials:** guest/guest

**Queues:**
- `embedding_queue` - Document embedding tasks
- `export_queue` - Data export/import jobs
- `workflow_queue` - Workflow execution
- `analytics_queue` - Analytics processing
- `dead_letter_queue` - Failed tasks

### 4. Admin Dashboard

Web-based administration interface.

**Access:** http://localhost/admin

**Features:**
- Organization management
- User administration
- System health monitoring
- Analytics and reporting
- Model management

## Multi-tenancy Usage

### Create Organization

```bash
curl -X POST http://localhost/api/organizations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Company",
    "plan": "enterprise"
  }'
```

### Create Workspace

```bash
curl -X POST http://localhost/api/organizations/{org_id}/workspaces \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Project Alpha",
    "slug": "project-alpha",
    "description": "Main project workspace"
  }'
```

### Invite Team Member

```bash
curl -X POST http://localhost/api/organizations/{org_id}/members \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "role": "admin"
  }'
```

### List Organizations

```bash
curl http://localhost/api/organizations \
  -H "Authorization: Bearer $TOKEN"
```

## Custom Model Integration

### Upload Custom Model

```bash
curl -X POST http://localhost/api/models/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "model_file=@custom_model.bin" \
  -F "config=@model_config.json"
```

### Model Config Format

```json
{
  "name": "custom-bert-model",
  "type": "custom",
  "dimension": 768,
  "max_sequence_length": 512,
  "pooling": "mean",
  "normalization": true
}
```

### List Models

```bash
curl http://localhost/api/models?organization_id={org_id} \
  -H "Authorization: Bearer $TOKEN"
```

### Activate Model

```bash
curl -X POST http://localhost/api/models/{model_id}/activate \
  -H "Authorization: Bearer $TOKEN"
```

### Embed with Specific Model

```bash
curl -X POST http://localhost/api/embed \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Text to embed"],
    "model_id": "{model_id}",
    "workspace_id": "{workspace_id}"
  }'
```

## Data Export/Import

### Export Collections

```bash
curl -X POST http://localhost/api/export/collections \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "{workspace_id}",
    "collections": ["collection1", "collection2"],
    "format": "json",
    "include_vectors": true
  }'
```

**Response:**
```json
{
  "export_id": "uuid",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Check Export Status

```bash
curl http://localhost/api/exports/{export_id} \
  -H "Authorization: Bearer $TOKEN"
```

### Download Export

```bash
curl http://localhost/api/exports/{export_id}/download \
  -H "Authorization: Bearer $TOKEN" \
  -o export.json
```

### Import Collections

```bash
curl -X POST http://localhost/api/import/collections \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@export.json" \
  -F "workspace_id={workspace_id}"
```

### Create Backup

```bash
curl -X POST http://localhost/api/backups \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "{workspace_id}",
    "type": "full"
  }'
```

### List Backups

```bash
curl http://localhost/api/backups?workspace_id={workspace_id} \
  -H "Authorization: Bearer $TOKEN"
```

### Restore Backup

```bash
curl -X POST http://localhost/api/backups/{backup_id}/restore \
  -H "Authorization: Bearer $TOKEN"
```

## Analytics

### Usage Statistics

```bash
curl "http://localhost/api/analytics/usage?org_id={org_id}&start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "organization_id": "uuid",
  "period": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "metrics": {
    "api_calls": 10000,
    "embeddings_generated": 5000,
    "searches_performed": 3000,
    "storage_used_gb": 25.5,
    "active_users": 15
  },
  "top_endpoints": [
    {
      "endpoint": "/api/embed",
      "count": 5000
    }
  ]
}
```

### Performance Metrics

```bash
curl http://localhost/api/analytics/performance?workspace_id={workspace_id} \
  -H "Authorization: Bearer $TOKEN"
```

### Cost Breakdown

```bash
curl "http://localhost/api/analytics/costs?org_id={org_id}&period=2024-01" \
  -H "Authorization: Bearer $TOKEN"
```

### Generate Custom Report

```bash
curl -X POST http://localhost/api/analytics/reports \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "usage",
    "organization_id": "{org_id}",
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-01-31"
    },
    "format": "pdf"
  }'
```

## RabbitMQ Workers

### Embedding Worker

Processes document embedding tasks asynchronously.

**Monitor Queue:**
```bash
# View queue stats
curl http://localhost:15672/api/queues/%2F/embedding_queue \
  -u guest:guest
```

**Task Format:**
```json
{
  "workspace_id": "uuid",
  "collection_name": "my_collection",
  "texts": ["text1", "text2"],
  "model_id": "uuid",
  "user_id": "uuid"
}
```

### Export Worker

Processes data export and import jobs.

**Task Format:**
```json
{
  "export_id": "uuid",
  "workspace_id": "uuid",
  "collections": ["col1", "col2"],
  "format": "json",
  "include_vectors": true,
  "user_id": "uuid"
}
```

## Database Schema

### Key Tables

- **organizations** - Organization/tenant data
- **workspaces** - Projects within organizations
- **users** - User accounts
- **organization_members** - Organization memberships
- **workspace_members** - Workspace access control
- **collections** - Vector collections scoped to workspaces
- **models** - Custom model registry
- **api_usage** - API call tracking
- **embedding_operations** - Embedding operation logs
- **audit_logs** - Audit trail
- **backups** - Backup metadata
- **exports** - Export job metadata

### View Schema

```bash
psql -h localhost -U ragamuffin -d ragamuffin -c "\dt"
```

## Security

### Environment Variables

Update these in production:

```bash
# .env
POSTGRES_PASSWORD=<strong-password>
JWT_SECRET_KEY=<random-secret>
TRAEFIK_DASHBOARD_PASSWORD=<hashed-password>
```

### Generate Secure Passwords

```bash
# JWT Secret
openssl rand -hex 32

# Traefik Password (htpasswd)
htpasswd -nb admin <password>
```

### Database Backups

```bash
# Manual backup
docker exec ragamuffin-postgres pg_dump -U ragamuffin ragamuffin > backup.sql

# Restore
cat backup.sql | docker exec -i ragamuffin-postgres psql -U ragamuffin -d ragamuffin
```

## Monitoring

### Traefik Dashboard

**Access:** http://localhost:8090

View:
- Active routes
- Service health
- Request metrics
- Error rates

### RabbitMQ Management

**Access:** http://localhost:15672

View:
- Queue depths
- Message rates
- Consumer status
- Dead letter queues

### PostgreSQL Monitoring

```bash
# Active connections
psql -h localhost -U ragamuffin -d ragamuffin -c "SELECT count(*) FROM pg_stat_activity;"

# Database size
psql -h localhost -U ragamuffin -d ragamuffin -c "SELECT pg_size_pretty(pg_database_size('ragamuffin'));"

# Table sizes
psql -h localhost -U ragamuffin -d ragamuffin -c "
SELECT 
    schemaname as schema,
    tablename as table,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

## Troubleshooting

### Check Service Status

```bash
docker-compose ps
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f postgres
docker-compose logs -f rabbitmq
docker-compose logs -f traefik
docker-compose logs -f embedding-worker
```

### Reset Database

```bash
# Stop services
docker-compose down

# Remove volume
docker volume rm rag7_postgres_data

# Restart
docker-compose up -d postgres
```

### Clear RabbitMQ Queues

```bash
# Purge a queue
curl -X DELETE http://localhost:15672/api/queues/%2F/embedding_queue/contents \
  -u guest:guest
```

### Traefik Configuration Test

```bash
# Validate config
docker exec ragamuffin-traefik traefik version

# View active routes
curl http://localhost:8090/api/http/routers | jq
```

## Production Deployment

### Checklist

1. **Security:**
   - [ ] Change all default passwords
   - [ ] Generate strong JWT secret
   - [ ] Configure SSL/TLS in Traefik
   - [ ] Enable firewall rules
   - [ ] Set up backup encryption

2. **Scaling:**
   - [ ] Configure PostgreSQL connection pooling
   - [ ] Add more RabbitMQ nodes for HA
   - [ ] Set up read replicas
   - [ ] Configure Traefik load balancing

3. **Monitoring:**
   - [ ] Set up Prometheus alerts
   - [ ] Configure log aggregation
   - [ ] Set up uptime monitoring
   - [ ] Enable audit logging

4. **Backups:**
   - [ ] Automated database backups
   - [ ] Offsite backup storage
   - [ ] Test restore procedures
   - [ ] Document recovery process

### Environment-Specific Configs

Create separate compose files:
- `docker-compose.yml` - Development
- `docker-compose.staging.yml` - Staging
- `docker-compose.prod.yml` - Production

## Support

For issues and questions:
- Check logs: `docker-compose logs -f`
- Review documentation: `ENTERPRISE_FEATURES.md`
- Database schema: `postgres/init/01_schema.sql`
- API reference: `docs/API_REFERENCE.md`

## Next Steps

1. Explore the Admin Dashboard at http://localhost/admin
2. Create your first organization and workspace
3. Upload a custom embedding model
4. Export and import your data
5. View analytics and usage reports
