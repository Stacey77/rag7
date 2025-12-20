# Run Commands

This document describes how to start, stop, and interact with the Epic Platform monorepo services.

## Prerequisites

- Docker (v20.10+)
- Docker Compose (v2.0+)
- 4GB+ available RAM
- Ports 7860, 8000, 8080 available

## Starting the Platform

### Using Shell Scripts (Recommended)

```bash
# Start all services in the background
./start-dev.sh

# Stop all services
./stop-dev.sh
```

### Using Docker Compose Directly

```bash
# Start all services
docker compose up -d

# Start with rebuild
docker compose up -d --build

# View logs
docker compose logs -f

# View logs for specific service
docker compose logs -f backend

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v
```

## Service URLs

Once started, access services at:

- **LangFlow UI**: http://localhost:7860
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend UI**: http://localhost:8080

## Individual Service Commands

### LangFlow

```bash
# Start only LangFlow
docker compose up -d langflow

# View LangFlow logs
docker compose logs -f langflow

# Restart LangFlow
docker compose restart langflow
```

### Backend

```bash
# Start only backend (requires langflow running)
docker compose up -d backend

# View backend logs
docker compose logs -f backend

# Restart backend
docker compose restart backend

# Access backend shell
docker compose exec backend /bin/bash
```

### Frontend

```bash
# Start only frontend
docker compose up -d frontend

# View frontend logs
docker compose logs -f frontend

# Restart frontend
docker compose restart frontend
```

## Development Workflow

### Rebuilding After Code Changes

```bash
# Rebuild specific service
docker compose build backend
docker compose up -d backend

# Rebuild all services
docker compose build
docker compose up -d
```

### Checking Service Health

```bash
# Check running containers
docker compose ps

# Check all containers (including stopped)
docker compose ps -a

# View resource usage
docker stats
```

### Debugging

```bash
# View recent logs
docker compose logs --tail=100

# Follow logs for all services
docker compose logs -f

# Execute command in running container
docker compose exec backend python -c "import langflow; print('LangFlow available')"

# Inspect container
docker compose exec backend env
```

## Data Management

### Flows Directory

Saved flows are stored in `./langflow-backend/flows` and mounted into the backend container.

```bash
# List saved flows
ls -la ./langflow-backend/flows/

# Backup flows
tar -czf flows-backup-$(date +%Y%m%d).tar.gz ./langflow-backend/flows/
```

### LangFlow Data

LangFlow data is stored in a Docker volume.

```bash
# Inspect volume
docker volume inspect rag7_langflow-data

# Backup volume
docker run --rm -v rag7_langflow-data:/data -v $(pwd):/backup ubuntu tar czf /backup/langflow-data-backup.tar.gz -C /data .

# Restore volume
docker run --rm -v rag7_langflow-data:/data -v $(pwd):/backup ubuntu tar xzf /backup/langflow-data-backup.tar.gz -C /data
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :7860
lsof -i :8000
lsof -i :8080

# Kill process
kill -9 <PID>
```

### Container Won't Start

```bash
# Remove and recreate
docker compose down
docker compose up -d --force-recreate

# Check logs for errors
docker compose logs backend
```

### Out of Memory

```bash
# Check Docker resources
docker system df

# Clean up unused resources
docker system prune -a --volumes
```

### Reset Everything

```bash
# Complete reset (WARNING: removes all data)
docker compose down -v
docker system prune -a --volumes
rm -rf ./langflow-backend/flows/*
./start-dev.sh
```

## Production Deployment

For production deployment, consider:

1. Use environment-specific compose files
2. Configure proper CORS origins
3. Add authentication/authorization
4. Use secrets management
5. Implement SSL/TLS
6. Set up monitoring and logging
7. Configure resource limits
8. Use managed database services

Example production override:

```bash
# Create docker-compose.prod.yml
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
