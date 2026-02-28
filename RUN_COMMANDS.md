# Ragamuffin Run Commands

## Prerequisites

- Docker and Docker Compose installed
- Node.js 18+ (for local frontend development)
- Python 3.10+ (for local backend development)

## Quick Start

### Start All Services

```bash
# Using the convenience script
./start-dev.sh

# Or directly with Docker Compose
docker compose up --build
```

### Stop All Services

```bash
# Using the convenience script
./stop-dev.sh

# Or directly with Docker Compose
docker compose down
```

## Individual Service Commands

### LangFlow (Port 7860)

```bash
# Build and run LangFlow container
docker compose up --build langflow

# Or run locally
pip install langflow
langflow run --host 0.0.0.0 --port 7860
```

### Backend (Port 8000)

```bash
# Build and run backend container
docker compose up --build backend

# Or run locally
cd langflow-backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (Port 8080)

```bash
# Build and run frontend container
docker compose up --build frontend

# Or run locally
cd web-client
npm install
npm run dev
```

### LangGraph (Port 7878)

```bash
# Build and run LangGraph container
docker compose up --build langgraph

# Or run locally
pip install langgraph langgraph-cli
langgraph dev --port 7878
```

## Development Workflow

### Rebuild a Specific Service

```bash
docker compose up --build <service-name>
# Example: docker compose up --build backend
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
```

### Enter Container Shell

```bash
docker compose exec backend /bin/bash
```

### Clean Up

```bash
# Remove containers and networks
docker compose down

# Remove containers, networks, and volumes
docker compose down -v

# Remove all images
docker compose down --rmi all
```

## Environment Variables

### Frontend (.env)

```
VITE_API_URL=http://localhost:8000
```

### Backend

Configure in `docker-compose.yml` or create `langflow-backend/.env`:

```
DEBUG=true
FLOWS_DIR=/app/flows
```

## Testing

### Backend

```bash
cd langflow-backend
pip install pytest httpx
pytest
```

### Frontend

```bash
cd web-client
npm run test
```

## Production Deployment

⚠️ **Before production deployment:**

1. Update CORS settings in `langflow-backend/app/main.py`
2. Add authentication (JWT/OAuth)
3. Use a database for flow persistence
4. Configure proper SSL/TLS
5. Set production environment variables
