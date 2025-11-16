# Run Commands - Step by Step Guide

This document provides detailed commands for running and managing the Epic Platform.

## 🚀 Quick Start (Recommended)

### Start All Services
```bash
./start-dev.sh
```

This script runs `docker compose up --build` and starts:
- LangFlow on http://localhost:7860
- Backend API on http://localhost:8000
- Frontend on http://localhost:8080

### Stop All Services
```bash
./stop-dev.sh
```

This script runs `docker compose down` and stops all containers.

---

## 🔧 Manual Commands

### First Time Setup

```bash
# Ensure you're in the repository root
cd /path/to/rag7

# Make scripts executable (if not already)
chmod +x start-dev.sh stop-dev.sh
```

### Build Services

```bash
# Build all services
docker compose build

# Build specific service
docker compose build langflow
docker compose build backend
docker compose build frontend

# Build without cache (clean rebuild)
docker compose build --no-cache
```

### Start Services

```bash
# Start all services (with build)
docker compose up --build

# Start in detached mode (background)
docker compose up -d

# Start specific service
docker compose up langflow
docker compose up backend
docker compose up frontend
```

### Stop Services

```bash
# Stop all services (keeps containers)
docker compose stop

# Stop and remove containers
docker compose down

# Stop and remove containers, volumes, images
docker compose down -v --rmi all
```

### View Logs

```bash
# View logs for all services
docker compose logs

# Follow logs (real-time)
docker compose logs -f

# View logs for specific service
docker compose logs backend
docker compose logs -f frontend

# Last 100 lines
docker compose logs --tail=100
```

### Service Management

```bash
# Restart specific service
docker compose restart backend

# Restart all services
docker compose restart

# Check service status
docker compose ps

# Execute command in running container
docker compose exec backend bash
docker compose exec frontend sh
```

## 🧪 Development Commands

### Backend Development

```bash
# View backend logs
docker compose logs -f backend

# Access backend shell
docker compose exec backend bash

# Install new Python dependency
docker compose exec backend pip install <package>

# Restart backend after code changes
docker compose restart backend
```

### Frontend Development

```bash
# View frontend logs
docker compose logs -f frontend

# Access frontend shell (nginx container)
docker compose exec frontend sh

# Rebuild frontend after dependency changes
docker compose build frontend
docker compose up -d frontend
```

### LangFlow Development

```bash
# View LangFlow logs
docker compose logs -f langflow

# Access LangFlow shell
docker compose exec langflow bash

# Restart LangFlow
docker compose restart langflow
```

## 🔍 Debugging

### Check Service Health

```bash
# Check all services
docker compose ps

# Check specific service
docker compose ps backend

# Inspect service details
docker compose inspect backend
```

### Network Issues

```bash
# List networks
docker network ls

# Inspect epic-platform network
docker network inspect rag7_epic-platform

# Test connectivity between services
docker compose exec backend ping langflow
docker compose exec frontend ping backend
```

### Volume Management

```bash
# List volumes
docker volume ls

# Inspect flows volume
docker volume inspect rag7_flows

# Backup flows
docker compose cp backend:/app/flows ./backup-flows
```

## 🧹 Cleanup

### Remove Stopped Containers
```bash
docker compose rm
```

### Full Cleanup
```bash
# Stop and remove everything
docker compose down -v

# Remove dangling images
docker image prune

# Remove all unused resources
docker system prune -a
```

## 🌐 Access URLs

After starting services:

- **LangFlow UI**: http://localhost:7860
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **Frontend App**: http://localhost:8080

## ⚙️ Environment Variables

### Backend
Environment variables can be set in `docker-compose.yml` or `.env` file:
```bash
PYTHONUNBUFFERED=1
# Add custom vars here
```

### Frontend
Environment variables in `web-client/.env`:
```bash
VITE_API_URL=http://localhost:8000
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000
lsof -i :7860
lsof -i :8080

# Kill process
kill -9 <PID>
```

### Container Won't Start
```bash
# Check logs
docker compose logs <service>

# Remove and rebuild
docker compose down
docker compose up --build
```

### Flows Not Persisting
```bash
# Check volume mount
docker compose config | grep volumes

# Verify flows directory exists
ls -la ./langflow-backend/flows/
```

---

## 📋 Common Workflows

### Workflow 1: Fresh Start
```bash
./stop-dev.sh
docker compose build --no-cache
./start-dev.sh
```

### Workflow 2: Update Backend Code
```bash
# Code changes made to langflow-backend/
docker compose restart backend
docker compose logs -f backend
```

### Workflow 3: Update Frontend Code
```bash
# Code changes made to web-client/
docker compose build frontend
docker compose up -d frontend
docker compose logs -f frontend
```

### Workflow 4: Clean Restart
```bash
./stop-dev.sh
docker compose down -v
./start-dev.sh
```

---

For more information, see [README_MONOREPO.md](./README_MONOREPO.md)
