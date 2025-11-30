# Run Commands - Epic Platform

This document provides step-by-step commands to run the Epic Platform monorepo.

## Prerequisites

Before starting, ensure you have:

1. **Docker** installed (version 20.10 or higher)
2. **Docker Compose** installed (version 2.0 or higher)
3. At least **4GB of available RAM**
4. Ports **3000**, **7860**, and **8000** are available

### Verify Prerequisites

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# Check available ports
lsof -i :3000
lsof -i :7860
lsof -i :8000
# (These should return empty if ports are available)
```

## Starting the Platform

### Method 1: Using Helper Script (Recommended)

```bash
# Make the script executable (first time only)
chmod +x start-dev.sh

# Start all services
./start-dev.sh
```

### Method 2: Using Docker Compose Directly

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up --build -d
```

### Method 3: Build First, Then Start

```bash
# Step 1: Build all images
docker-compose build

# Step 2: Start all services
docker-compose up

# Or in detached mode
docker-compose up -d
```

## Monitoring Services

### View Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for a specific service
docker-compose logs frontend
docker-compose logs backend
docker-compose logs langflow

# Follow logs for a specific service
docker-compose logs -f backend
```

### Check Service Status

```bash
# List running containers
docker-compose ps

# Check if services are healthy
docker ps
```

## Accessing Services

Once all services are running:

### Frontend (React Web Client)
- **URL**: http://localhost:3000
- **Pages**:
  - Dashboard: http://localhost:3000/
  - Agent Builder: http://localhost:3000/agent-builder
  - Playground: http://localhost:3000/playground
  - Datasets: http://localhost:3000/datasets

### Backend (FastAPI)
- **URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Health Check**: http://localhost:8000/

**Available Endpoints**:
```bash
# List all flows
curl http://localhost:8000/list_flows/

# Get a specific flow
curl http://localhost:8000/get_flow/my_flow

# Save a flow (POST with JSON)
curl -X POST http://localhost:8000/save_flow/ \
  -H "Content-Type: application/json" \
  -d '{"flow_name": "test_flow", "flow_data": {...}}'

# Run a flow
curl -X POST http://localhost:8000/run_flow/ \
  -H "Content-Type: application/json" \
  -d '{"flow_data": {...}, "user_input": "Hello"}'
```

### LangFlow (Visual Builder)
- **URL**: http://localhost:7860
- **Description**: Drag-and-drop interface for building AI workflows

## Stopping the Platform

### Method 1: Using Helper Script

```bash
# Stop all services and remove containers
./stop-dev.sh
```

### Method 2: Using Docker Compose

```bash
# Stop services (Ctrl+C if running in foreground)

# Stop and remove containers
docker-compose down

# Stop, remove containers, and remove volumes (CAUTION: deletes data)
docker-compose down -v

# Stop, remove everything including images
docker-compose down --rmi all -v
```

### Method 3: Stop Individual Services

```bash
# Stop a specific service
docker-compose stop frontend
docker-compose stop backend
docker-compose stop langflow

# Start a specific service
docker-compose start frontend
```

## Rebuilding After Changes

### Rebuild All Services

```bash
# Rebuild all images
docker-compose build

# Rebuild and restart
docker-compose up --build
```

### Rebuild Specific Service

```bash
# Rebuild only the frontend
docker-compose build frontend

# Rebuild and restart frontend
docker-compose up --build frontend
```

### Force Rebuild (No Cache)

```bash
# Rebuild without using cache
docker-compose build --no-cache

# Rebuild specific service without cache
docker-compose build --no-cache backend
```

## Development Workflow

### 1. Start Development Environment

```bash
./start-dev.sh
# Wait for all services to be ready (check logs)
```

### 2. Make Changes

- **Backend**: Edit files in `langflow-backend/app/`
  - Changes are auto-reloaded (volume mounted)
  
- **Frontend**: Edit files in `web-client/src/`
  - Requires rebuild: `docker-compose build frontend && docker-compose up -d frontend`
  - Or run locally: `cd web-client && npm run dev`

### 3. Test Changes

```bash
# View logs to check for errors
docker-compose logs -f backend

# Test API endpoints
curl http://localhost:8000/docs

# Open frontend in browser
open http://localhost:3000
```

### 4. Stop When Done

```bash
./stop-dev.sh
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 3000
lsof -i :3000

# Kill the process (replace PID with actual process ID)
kill -9 <PID>

# Or use a different port in docker-compose.yml
# Change "3000:80" to "3001:80" for frontend
```

### Service Won't Start

```bash
# Check logs for errors
docker-compose logs <service-name>

# Remove containers and try again
docker-compose down
docker-compose up --build
```

### Out of Memory

```bash
# Check Docker memory allocation
docker system df

# Prune unused resources
docker system prune -a

# Increase Docker memory limit in Docker Desktop settings
```

### Reset Everything

```bash
# Stop all services
docker-compose down -v

# Remove all images
docker-compose down --rmi all -v

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up
```

## Running Individual Services Locally (Without Docker)

### Backend (FastAPI)

```bash
cd langflow-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (React)

```bash
cd web-client

# Install dependencies
npm install

# Run development server
npm run dev
# Opens on http://localhost:5173 by default
```

### LangFlow

```bash
# Install LangFlow
pip install langflow

# Run LangFlow
langflow run --host 0.0.0.0 --port 7860
```

## Environment Variables

### Backend

Create `langflow-backend/.env`:
```
LANGFLOW_URL=http://langflow:7860
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend

Create `web-client/.env`:
```
VITE_API_URL=http://localhost:8000
```

## Next Steps

1. **Explore the platform**: Visit http://localhost:3000
2. **Create a flow**: Use LangFlow at http://localhost:7860
3. **Test the API**: Check http://localhost:8000/docs
4. **Build an agent**: Use the Agent Builder page
5. **Customize**: Modify components in `web-client/src/`

## Getting Help

- Check the logs: `docker-compose logs -f`
- Review README_MONOREPO.md for architecture details
- Check individual service READMEs in their directories
