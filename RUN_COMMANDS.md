# Run Commands Guide

This guide provides step-by-step instructions for running and developing with the Ragamuffin monorepo.

## Prerequisites

Ensure you have the following installed:
- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- Git

Verify installations:
```bash
docker --version
docker compose version
git --version
```

## First-Time Setup

### 1. Clone the Repository

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

The flows directory should exist, but verify:
```bash
ls -la langflow-backend/flows/
```

## Development Commands

### Start All Services

Start the entire stack (LangFlow, Backend, Frontend):

```bash
./start-dev.sh
```

Or manually:
```bash
docker compose up --build
```

Add `-d` flag to run in detached mode:
```bash
docker compose up --build -d
```

### Stop All Services

```bash
./stop-dev.sh
```

Or manually:
```bash
docker compose down
```

To also remove volumes:
```bash
docker compose down -v
```

### View Logs

View logs from all services:
```bash
docker compose logs -f
```

View logs from specific service:
```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f langflow
```

### Restart a Specific Service

```bash
docker compose restart backend
docker compose restart frontend
docker compose restart langflow
```

### Rebuild After Code Changes

If you modify code in any service:

```bash
docker compose up --build
```

Or rebuild specific service:
```bash
docker compose up --build backend
```

### Access Services

Once running, access the services at:
- **LangFlow UI**: http://localhost:7860
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend Application**: http://localhost:8080

## Service-Specific Development

### Backend Development

Run backend outside Docker for faster iteration:

```bash
cd langflow-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

Run frontend outside Docker for hot-reloading:

```bash
cd web-client
npm install
npm run dev
```

This starts the Vite dev server with hot module replacement.

### LangFlow Development

Run LangFlow standalone:

```bash
pip install langflow
langflow run --host 0.0.0.0 --port 7860
```

## Testing Backend Endpoints

### Save a Flow

```bash
curl -X POST "http://localhost:8000/save_flow/" \
  -F "flow_file=@path/to/your/flow.json"
```

### List All Flows

```bash
curl -X GET "http://localhost:8000/list_flows/"
```

### Get a Specific Flow

```bash
curl -X GET "http://localhost:8000/get_flow/my_flow"
```

### Run a Flow

```bash
curl -X POST "http://localhost:8000/run_flow/" \
  -F "flow_file=@path/to/your/flow.json" \
  -F "user_input=Hello, how are you?"
```

## Troubleshooting

### Port Already in Use

If ports are already in use, modify `docker-compose.yml`:

```yaml
ports:
  - "7861:7860"  # Change host port
  - "8001:8000"  # Change host port
  - "8081:80"    # Change host port
```

Also update `.env` in web-client accordingly.

### Docker Build Fails

Clear Docker cache and rebuild:

```bash
docker compose down
docker system prune -a
docker compose up --build
```

### Backend Not Connecting to LangFlow

Ensure services are on the same network:

```bash
docker network inspect rag7_ragamuffin-network
```

### Frontend Can't Reach Backend

Check CORS settings in `langflow-backend/app/main.py` and verify the API URL in `web-client/.env`.

### Flows Directory Permission Issues

Ensure the flows directory has proper permissions:

```bash
chmod 777 langflow-backend/flows/
```

## Advanced Commands

### Execute Commands in Running Container

```bash
docker compose exec backend bash
docker compose exec frontend sh
docker compose exec langflow bash
```

### View Container Resource Usage

```bash
docker stats
```

### Clean Up Everything

Remove all containers, volumes, and images:

```bash
docker compose down -v
docker system prune -a --volumes
```

**Warning**: This removes ALL Docker resources, not just this project.

## Environment Variables

### Backend

Set in `docker-compose.yml` or create `.env` file:
- `LANGFLOW_HOST`: LangFlow service hostname (default: langflow)
- `LANGFLOW_PORT`: LangFlow port (default: 7860)

### Frontend

Set in `web-client/.env`:
- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)

## Production Deployment

For production deployment:

1. Use proper environment variables
2. Configure reverse proxy (nginx/traefik)
3. Enable HTTPS
4. Set up proper logging
5. Configure health checks
6. Use production-grade database
7. Implement authentication
8. Set resource limits in docker-compose.yml

Example resource limits:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Getting Help

- Check service logs: `docker compose logs -f`
- Verify service status: `docker compose ps`
- Check API docs: http://localhost:8000/docs
- Review individual service READMEs in their directories

## Next Steps

After getting the services running:

1. Visit LangFlow at http://localhost:7860 to create a workflow
2. Export the flow as JSON
3. Upload it via the Frontend Agent Builder at http://localhost:8080
4. Test the flow execution through the Playground

Enjoy building with Ragamuffin! 🚀
