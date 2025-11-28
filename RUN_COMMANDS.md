# Ragamuffin Platform - Run Commands

This document provides step-by-step commands for running and developing the Ragamuffin platform.

## Prerequisites Check

### 1. Verify Docker Installation
```bash
docker --version
docker-compose --version
```
Expected: Docker 20.10+ and Docker Compose 1.29+

### 2. Check Port Availability
```bash
# Check if required ports are free
netstat -an | grep -E ':(7860|8000|8080)'
```
If ports are in use, stop the conflicting services or modify port mappings in `docker-compose.yml`.

## First-Time Setup

### 1. Clone Repository
```bash
git clone https://github.com/Stacey77/rag7.git
cd rag7
git checkout ragamuffin-scaffold
```

### 2. Make Scripts Executable
```bash
chmod +x start-dev.sh stop-dev.sh
```

### 3. Create Required Directories
```bash
mkdir -p langflow-backend/flows
```

## Starting the Platform

### Option 1: Using the Quick Start Script
```bash
./start-dev.sh
```
This will:
- Build all Docker images
- Start all services (langflow, backend, frontend)
- Automatically create the network

### Option 2: Manual Docker Compose
```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

### Option 3: Start Individual Services
```bash
# Start only langflow
docker-compose up langflow

# Start only backend
docker-compose up backend

# Start only frontend
docker-compose up frontend
```

## Accessing Services

Once services are running:

- **Web Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **Backend API Docs**: http://localhost:8000/docs (Swagger UI)
- **Backend API Redoc**: http://localhost:8000/redoc
- **LangFlow UI**: http://localhost:7860

## Development Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f langflow
```

### Rebuild After Code Changes
```bash
# Rebuild all services
docker-compose up --build

# Rebuild specific service
docker-compose up --build backend
```

### Execute Commands in Containers
```bash
# Access backend container shell
docker exec -it ragamuffin-backend bash

# Access frontend container shell
docker exec -it ragamuffin-frontend sh

# Access langflow container shell
docker exec -it ragamuffin-langflow bash
```

### Check Container Status
```bash
docker-compose ps
```

### View Resource Usage
```bash
docker stats
```

## Backend API Testing

### Test Backend Endpoints
```bash
# List flows
curl http://localhost:8000/list_flows/

# Get specific flow
curl http://localhost:8000/get_flow/my_flow.json

# Upload a flow (create a test flow first)
echo '{"nodes": [], "edges": []}' > test_flow.json
curl -X POST -F "flow_file=@test_flow.json" http://localhost:8000/save_flow/

# Run a flow
curl -X POST -F "flow_file=@test_flow.json" -F "user_input=Hello" http://localhost:8000/run_flow/
```

## Stopping the Platform

### Option 1: Using the Stop Script
```bash
./stop-dev.sh
```

### Option 2: Manual Docker Compose
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (careful: deletes data!)
docker-compose down -v
```

### Option 3: Stop Without Removing Containers
```bash
docker-compose stop
```

## Development Workflow

### Frontend Development
```bash
# If you want to develop frontend without Docker:
cd web-client
npm install
npm run dev
# Access at http://localhost:5173
# Update .env to point to backend: VITE_API_URL=http://localhost:8000
```

### Backend Development
```bash
# If you want to develop backend without Docker:
cd langflow-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### LangFlow Development
```bash
# Run LangFlow directly:
pip install langflow
langflow run --host 0.0.0.0 --port 7860
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8080  # or :8000, :7860

# Kill the process
kill -9 <PID>
```

### Docker Build Issues
```bash
# Clear Docker cache
docker-compose build --no-cache

# Remove all containers and rebuild
docker-compose down
docker-compose up --build
```

### Permission Issues
```bash
# Fix permissions for flows directory
sudo chown -R $USER:$USER langflow-backend/flows
chmod -R 755 langflow-backend/flows
```

### Container Won't Start
```bash
# Check logs for specific service
docker-compose logs backend

# Inspect container
docker inspect ragamuffin-backend

# Remove and recreate
docker-compose rm -f backend
docker-compose up --build backend
```

### Network Issues
```bash
# Recreate network
docker-compose down
docker network prune
docker-compose up
```

## Production Deployment Considerations

For production deployment:

1. **Environment Variables**: Use `.env` files or secret management
2. **Reverse Proxy**: Add nginx/traefik in front of services
3. **HTTPS**: Configure TLS certificates
4. **Authentication**: Implement OAuth2/JWT
5. **Monitoring**: Add Prometheus, Grafana
6. **Logging**: Centralized logging with ELK/Loki
7. **Backups**: Regular backups of flows directory
8. **Scaling**: Use Docker Swarm or Kubernetes

## Clean Up

### Remove Everything
```bash
# Stop and remove containers, networks, volumes
docker-compose down -v

# Remove images
docker rmi $(docker images 'ragamuffin*' -q)

# Remove dangling images
docker image prune -f
```

## Getting Help

- Check service logs: `docker-compose logs -f <service>`
- Verify network connectivity: `docker network inspect rag7_ragamuffin-network`
- Review API documentation: http://localhost:8000/docs
- Test endpoints with Swagger UI: http://localhost:8000/docs
