# Enterprise Features Implementation

## Overview

This document outlines the comprehensive enterprise features added to the Ragamuffin platform.

## Services Added

### 1. Traefik API Gateway
- **Port**: 80 (HTTP), 443 (HTTPS), 8080 (Dashboard)
- **Purpose**: Unified API management, routing, and load balancing
- **Features**:
  - Automatic service discovery
  - SSL/TLS termination with Let's Encrypt
  - Request tracing and logging
  - Rate limiting and circuit breakers
  - Health checks

### 2. RabbitMQ Message Queue
- **Port**: 5672 (AMQP), 15672 (Management UI)
- **Purpose**: Async task processing
- **Queues**:
  - `embedding_queue` - Document embedding tasks
  - `workflow_queue` - n8n workflow execution
  - `export_queue` - Data export jobs
  - `analytics_queue` - Analytics processing
- **Login**: guest/guest

### 3. PostgreSQL Database
- **Port**: 5432
- **Purpose**: Persistent data storage
- **Databases**:
  - `ragamuffin` - Main application database
  - `analytics` - Analytics and reporting
- **Schema**:
  - Organizations, Workspaces, Users
  - Audit logs, API usage tracking
  - Model registry, Backups metadata

## Multi-tenancy Architecture

### Database Schema

```sql
-- Organizations
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    plan VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    settings JSONB DEFAULT '{}'
);

-- Workspaces (Projects within organizations)
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users (extended from existing auth)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Organization memberships
CREATE TABLE organization_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    user_id UUID REFERENCES users(id),
    role VARCHAR(50) DEFAULT 'member', -- owner, admin, member
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organization_id, user_id)
);

-- Workspace memberships
CREATE TABLE workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id),
    user_id UUID REFERENCES users(id),
    role VARCHAR(50) DEFAULT 'contributor',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Collections (scoped to workspaces)
CREATE TABLE collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id),
    name VARCHAR(255) NOT NULL,
    model_id UUID REFERENCES models(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Models registry
CREATE TABLE models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50), -- sentence-transformer, openai, custom
    version VARCHAR(50),
    config JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API usage tracking
CREATE TABLE api_usage (
    id BIGSERIAL PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    user_id UUID REFERENCES users(id),
    endpoint VARCHAR(255),
    method VARCHAR(10),
    status_code INTEGER,
    duration_ms INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100),
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Backups metadata
CREATE TABLE backups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id),
    type VARCHAR(50), -- full, incremental
    status VARCHAR(50), -- pending, completed, failed
    size_bytes BIGINT,
    file_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### Organization Management

```python
# Create organization
POST /api/organizations
{
    "name": "Acme Corp",
    "plan": "enterprise"
}

# List organizations
GET /api/organizations

# Get organization details
GET /api/organizations/{org_id}

# Update organization
PUT /api/organizations/{org_id}

# Delete organization
DELETE /api/organizations/{org_id}

# Invite member
POST /api/organizations/{org_id}/members
{
    "email": "user@example.com",
    "role": "admin"
}

# List members
GET /api/organizations/{org_id}/members

# Update member role
PUT /api/organizations/{org_id}/members/{user_id}

# Remove member
DELETE /api/organizations/{org_id}/members/{user_id}
```

### Workspace Management

```python
# Create workspace
POST /api/organizations/{org_id}/workspaces
{
    "name": "Project Alpha",
    "description": "Main project workspace"
}

# List workspaces
GET /api/organizations/{org_id}/workspaces

# Get workspace
GET /api/workspaces/{workspace_id}

# Update workspace
PUT /api/workspaces/{workspace_id}

# Delete workspace
DELETE /api/workspaces/{workspace_id}

# Add workspace member
POST /api/workspaces/{workspace_id}/members
```

### Custom Model Management

```python
# Upload custom model
POST /api/models/upload
Content-Type: multipart/form-data
- model_file: binary
- config: JSON

# List models
GET /api/models?organization_id={org_id}

# Get model
GET /api/models/{model_id}

# Activate model
POST /api/models/{model_id}/activate

# Delete model
DELETE /api/models/{model_id}

# Embed with specific model
POST /api/embed
{
    "texts": ["text1", "text2"],
    "model_id": "uuid",
    "workspace_id": "uuid"
}
```

### Data Export/Import

```python
# Export collections
POST /api/export/collections
{
    "workspace_id": "uuid",
    "collections": ["col1", "col2"],
    "format": "json" | "parquet",
    "include_vectors": true
}

# Get export status
GET /api/exports/{export_id}

# Download export
GET /api/exports/{export_id}/download

# Import collections
POST /api/import/collections
Content-Type: multipart/form-data
- file: binary
- workspace_id: string

# List backups
GET /api/backups?workspace_id={workspace_id}

# Create backup
POST /api/backups
{
    "workspace_id": "uuid",
    "type": "full"
}

# Restore backup
POST /api/backups/{backup_id}/restore
```

### Analytics

```python
# Usage statistics
GET /api/analytics/usage?org_id={org_id}&start_date={date}&end_date={date}

# Performance metrics
GET /api/analytics/performance?workspace_id={workspace_id}

# Cost breakdown
GET /api/analytics/costs?org_id={org_id}&period={month}

# Generate report
POST /api/analytics/reports
{
    "type": "usage" | "performance" | "costs",
    "organization_id": "uuid",
    "date_range": {"start": "2024-01-01", "end": "2024-01-31"}
}

# Get report
GET /api/analytics/reports/{report_id}
```

## Admin Dashboard

### Features

1. **Organization Management**
   - View all organizations
   - Create/edit/delete organizations
   - Change organization plans
   - View organization statistics

2. **User Management**
   - View all users
   - Create/edit/deactivate users
   - Assign roles
   - View user activity

3. **System Health**
   - Service status monitoring
   - Resource usage (CPU, memory, disk)
   - Queue depths
   - Database connection pools

4. **Analytics Dashboard**
   - API usage charts
   - Embedding generation trends
   - Query performance metrics
   - Cost analysis

5. **Model Management**
   - View all models
   - Upload new models
   - Configure model parameters
   - Monitor model performance

6. **Audit Logs**
   - View all system actions
   - Filter by user, action, date
   - Export audit logs

### Routes

```typescript
/admin/
├── /organizations          # Organization list and management
├── /users                  # User management
├── /models                 # Model registry
├── /analytics             # Analytics dashboard
├── /system-health         # System monitoring
├── /audit-logs            # Audit log viewer
└── /settings              # System settings
```

## RabbitMQ Workers

### Embedding Worker

```python
# Process embedding tasks asynchronously
# Queue: embedding_queue

def process_embedding_task(task):
    workspace_id = task['workspace_id']
    texts = task['texts']
    model_id = task['model_id']
    
    # Load model
    model = load_model(model_id)
    
    # Generate embeddings
    embeddings = model.encode(texts)
    
    # Store in Milvus
    store_embeddings(workspace_id, embeddings)
    
    # Update analytics
    track_embedding_usage(workspace_id, len(texts))
```

### Export Worker

```python
# Process export tasks asynchronously
# Queue: export_queue

def process_export_task(task):
    workspace_id = task['workspace_id']
    collections = task['collections']
    format = task['format']
    
    # Export data
    export_file = export_collections(workspace_id, collections, format)
    
    # Store in object storage
    upload_to_storage(export_file)
    
    # Send notification
    notify_user(task['user_id'], export_file)
```

## Traefik Configuration

### Dynamic Routing

```yaml
http:
  routers:
    backend-router:
      rule: "PathPrefix(`/api`)"
      service: backend
      middlewares:
        - auth
        - rate-limit
    
    admin-router:
      rule: "PathPrefix(`/admin`)"
      service: admin-dashboard
      middlewares:
        - admin-auth
    
    rag-router:
      rule: "PathPrefix(`/rag`)"
      service: rag-service
      middlewares:
        - auth
        - rate-limit
  
  services:
    backend:
      loadBalancer:
        servers:
          - url: "http://backend:8000"
    
    admin-dashboard:
      loadBalancer:
        servers:
          - url: "http://admin-dashboard:3000"
    
    rag-service:
      loadBalancer:
        servers:
          - url: "http://rag-service:8001"
  
  middlewares:
    auth:
      forwardAuth:
        address: "http://backend:8000/verify-token"
    
    admin-auth:
      forwardAuth:
        address: "http://backend:8000/verify-admin"
    
    rate-limit:
      rateLimit:
        average: 100
        burst: 50
```

## Environment Variables

```bash
# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ragamuffin
POSTGRES_USER=ragamuffin
POSTGRES_PASSWORD=<secure-password>

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# Traefik
TRAEFIK_DASHBOARD_USER=admin
TRAEFIK_DASHBOARD_PASSWORD=<hashed-password>

# Multi-tenancy
DEFAULT_PLAN=free
MAX_WORKSPACES_FREE=3
MAX_WORKSPACES_PRO=10
MAX_WORKSPACES_ENTERPRISE=unlimited

# Custom Models
MAX_MODEL_SIZE_MB=500
SUPPORTED_MODEL_TYPES=sentence-transformer,openai,custom

# Analytics
ANALYTICS_RETENTION_DAYS=90
EXPORT_EXPIRY_DAYS=7
```

## Deployment

### Docker Compose Addition

```yaml
services:
  traefik:
    image: traefik:v2.10
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik/traefik.yml:/traefik.yml:ro
      - ./traefik/dynamic:/dynamic:ro
    labels:
      - "traefik.enable=true"
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ragamuffin
      POSTGRES_USER: ragamuffin
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./postgres/init:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
  
  rabbitmq:
    image: rabbitmq:3-management
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
      - ./rabbitmq/definitions.json:/etc/rabbitmq/definitions.json
    ports:
      - "5672:5672"
      - "15672:15672"
  
  admin-dashboard:
    build: ./admin-dashboard
    environment:
      REACT_APP_API_URL: http://backend:8000
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.admin.rule=PathPrefix(`/admin`)"
  
  embedding-worker:
    build: ./workers/embedding
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672
      DATABASE_URL: postgresql://ragamuffin:${POSTGRES_PASSWORD}@postgres:5432/ragamuffin
    depends_on:
      - rabbitmq
      - postgres
  
  export-worker:
    build: ./workers/export
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672
      DATABASE_URL: postgresql://ragamuffin:${POSTGRES_PASSWORD}@postgres:5432/ragamuffin
    depends_on:
      - rabbitmq
      - postgres

volumes:
  postgres-data:
  rabbitmq-data:
```

## Migration from In-Memory to PostgreSQL

### Step 1: Update Models

```python
# langflow-backend/app/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
```

### Step 2: Update Auth

```python
# langflow-backend/app/auth.py
from sqlalchemy.orm import Session
from app.models.user import User

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_data: dict):
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

## Testing

### Run Tests

```bash
# Test multi-tenancy
pytest tests/test_organizations.py
pytest tests/test_workspaces.py

# Test custom models
pytest tests/test_models.py

# Test export/import
pytest tests/test_export_import.py

# Test analytics
pytest tests/test_analytics.py

# Integration tests
pytest tests/integration/test_multitenancy_flow.py
```

## Monitoring

### Grafana Dashboards

1. **Multi-tenancy Dashboard**
   - Organizations count
   - Active workspaces
   - Users per organization
   - Resource usage by organization

2. **Queue Monitoring**
   - Queue depths
   - Message processing rate
   - Failed messages
   - Worker health

3. **Database Metrics**
   - Connection pool usage
   - Query performance
   - Table sizes
   - Index usage

## Security Considerations

1. **Data Isolation**: Enforce workspace-level data isolation at database level
2. **RBAC**: Implement role-based access control for all operations
3. **Audit Logging**: Log all administrative actions
4. **Rate Limiting**: Per-organization rate limiting
5. **API Keys**: Support API keys for programmatic access

## Next Steps

1. Implement database migrations with Alembic
2. Build React admin dashboard components
3. Configure Traefik dynamic routing
4. Implement RabbitMQ workers
5. Add comprehensive tests
6. Update documentation

## Conclusion

This enterprise feature set transforms Ragamuffin into a production-ready, multi-tenant RAG platform capable of serving multiple organizations with isolated workspaces, custom model support, and advanced analytics.
