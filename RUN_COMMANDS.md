# Ragamuffin Run Commands

This document provides all the commands needed to work with the Ragamuffin monorepo.

## 🚀 Quick Start Commands

### Start All Services
```bash
./start-dev.sh
```
This starts LangFlow (7860), Backend (8000), and Frontend (8080) services.

### Stop All Services
```bash
./stop-dev.sh
```
This stops and removes all running containers.

## 🐳 Docker Compose Commands

### Build and Start Services
```bash
docker compose up -d --build
```

### Start Services (without rebuild)
```bash
docker compose up -d
```

### Stop Services
```bash
docker compose down
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f langflow
```

### Rebuild Specific Service
```bash
docker compose build backend
docker compose build frontend
docker compose build langflow
```

### Restart Specific Service
```bash
docker compose restart backend
docker compose restart frontend
docker compose restart langflow
```

### Remove All Containers and Volumes
```bash
docker compose down -v
```

## 🔧 Development Commands

### Backend Development

#### Run Backend Locally (without Docker)
```bash
cd langflow-backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Test Backend Endpoints
```bash
# List flows
curl http://localhost:8000/list_flows/

# Get specific flow
curl http://localhost:8000/get_flow/my_flow

# Save flow (example)
curl -X POST http://localhost:8000/save_flow/ \
  -F "flow_name=test_flow" \
  -F "flow_json=@flow.json"

# Run flow (example)
curl -X POST http://localhost:8000/run_flow/ \
  -F "flow_json=@flow.json" \
  -F "user_input=Hello, agent!"
```

### Frontend Development

#### Run Frontend Locally (without Docker)
```bash
cd web-client
npm install
npm run dev
```

#### Build Frontend for Production
```bash
cd web-client
npm run build
```

#### Preview Production Build
```bash
cd web-client
npm run preview
```

### LangFlow Development

#### Access LangFlow UI
Open browser to: http://localhost:7860

## 📊 Monitoring Commands

### Check Service Status
```bash
docker compose ps
```

### Check Resource Usage
```bash
docker stats
```

### Inspect Network
```bash
docker network inspect rag7_ragamuffin-network
```

### Inspect Volumes
```bash
docker volume ls
docker volume inspect rag7_langflow_data
```

## 🧹 Cleanup Commands

### Remove Stopped Containers
```bash
docker compose rm
```

### Clean Build Cache
```bash
docker builder prune
```

### Remove Unused Images
```bash
docker image prune -a
```

### Full Cleanup (⚠️ removes all data)
```bash
docker compose down -v --rmi all
```

## 🔍 Debugging Commands

### Shell into Running Container
```bash
# Backend
docker compose exec backend /bin/bash

# Frontend
docker compose exec frontend /bin/sh

# LangFlow
docker compose exec langflow /bin/bash
```

### View Container Details
```bash
docker compose logs backend
docker inspect ragamuffin-backend
```

## 🌐 Service URLs

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **Backend Docs**: http://localhost:8000/docs
- **LangFlow**: http://localhost:7860

## 📝 Environment Variables

### Backend
- `LANGFLOW_URL`: URL to LangFlow service (default: http://langflow:7860)

### Frontend
- `VITE_API_URL`: URL to backend API (default: http://localhost:8000)

## 🎯 Common Workflows

### Workflow 1: Fresh Start
```bash
./stop-dev.sh
docker compose down -v
./start-dev.sh
```

### Workflow 2: Update Backend Code
```bash
docker compose build backend
docker compose up -d backend
docker compose logs -f backend
```

### Workflow 3: Update Frontend Code
```bash
docker compose build frontend
docker compose up -d frontend
```

### Workflow 4: Reset Everything
```bash
./stop-dev.sh
docker compose down -v --rmi all
./start-dev.sh
```
