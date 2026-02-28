# Run Commands Reference

This document provides all available commands for managing the Epic Platform.

## Quick Reference

```bash
./start-dev.sh          # Start all services
./stop-dev.sh           # Stop all services
```

## Docker Compose Commands

### Starting Services

```bash
# Start all services (detached)
docker-compose up -d

# Start all services with build
docker-compose up --build -d

# Start all services and view logs
docker-compose up

# Start specific service
docker-compose up -d langflow
docker-compose up -d backend
docker-compose up -d web-client
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop all services and remove volumes
docker-compose down -v

# Stop specific service
docker-compose stop langflow
```

### Viewing Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f langflow
docker-compose logs -f web-client

# View last 100 lines
docker-compose logs --tail=100 backend
```

### Service Management

```bash
# Restart a service
docker-compose restart backend

# Rebuild a service
docker-compose up -d --build backend

# Check service status
docker-compose ps

# Execute command in running container
docker-compose exec backend bash
docker-compose exec web-client sh
```

## Individual Service Commands

### LangFlow

```bash
# Access LangFlow
http://localhost:7860

# View LangFlow logs
docker-compose logs -f langflow

# Restart LangFlow
docker-compose restart langflow
```

### Backend API

```bash
# Access API documentation
http://localhost:8000/docs

# View backend logs
docker-compose logs -f backend

# Restart backend
docker-compose restart backend

# Execute commands in backend container
docker-compose exec backend bash

# Run backend locally (without Docker)
cd langflow-backend
pip install -r app/requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Web Client

```bash
# Access web interface
http://localhost:3000

# View web client logs
docker-compose logs -f web-client

# Restart web client
docker-compose restart web-client

# Run frontend locally (without Docker)
cd web-client
npm install
npm run dev
```

## Development Commands

### Frontend Development

```bash
cd web-client

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Type check
npm run type-check
```

### Backend Development

```bash
cd langflow-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r app/requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests (if available)
pytest
```

## API Testing

### Using curl

```bash
# Save a flow
curl -X POST "http://localhost:8000/save_flow/" \
  -H "Content-Type: application/json" \
  -d '{"flow_name": "test_flow", "flow_data": {"nodes": [], "edges": []}}'

# List all flows
curl http://localhost:8000/list_flows/

# Get a specific flow
curl http://localhost:8000/get_flow/test_flow

# Run a flow
curl -X POST "http://localhost:8000/run_flow/" \
  -H "Content-Type: application/json" \
  -d '{"flow_name": "test_flow", "input_data": {"message": "Hello"}}'
```

### Using httpie

```bash
# Save a flow
http POST localhost:8000/save_flow/ flow_name=test_flow flow_data:='{"nodes":[]}'

# List flows
http localhost:8000/list_flows/

# Get flow
http localhost:8000/get_flow/test_flow

# Run flow
http POST localhost:8000/run_flow/ flow_name=test_flow input_data:='{"message":"Hello"}'
```

## Debugging

### Check Container Status

```bash
# View all containers
docker ps -a

# Inspect a container
docker inspect epic-backend

# View container resource usage
docker stats
```

### Access Container Shell

```bash
# Backend
docker-compose exec backend bash

# Web Client
docker-compose exec web-client sh

# LangFlow
docker-compose exec langflow bash
```

### View Container Logs

```bash
# Real-time logs
docker-compose logs -f

# Logs since 10 minutes ago
docker-compose logs --since 10m

# Last 50 lines
docker-compose logs --tail=50
```

### Network Debugging

```bash
# List networks
docker network ls

# Inspect epic network
docker network inspect rag7_epic-network

# Test connectivity between containers
docker-compose exec backend ping langflow
docker-compose exec web-client wget -O- http://backend:8000/list_flows/
```

## Maintenance

### Clean Up

```bash
# Remove stopped containers
docker-compose rm

# Clean up unused images
docker image prune -a

# Clean up volumes
docker volume prune

# Complete cleanup (WARNING: removes all data)
docker-compose down -v
docker system prune -a
```

### Backup

```bash
# Backup flows directory
tar -czf flows-backup-$(date +%Y%m%d).tar.gz langflow-backend/flows/

# Backup LangFlow volume
docker run --rm -v rag7_langflow_data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/langflow-backup-$(date +%Y%m%d).tar.gz /data
```

### Restore

```bash
# Restore flows
tar -xzf flows-backup-YYYYMMDD.tar.gz -C langflow-backend/

# Restore LangFlow volume
docker run --rm -v rag7_langflow_data:/data -v $(pwd):/backup \
  ubuntu tar xzf /backup/langflow-backup-YYYYMMDD.tar.gz -C /
```

## Performance Monitoring

```bash
# Monitor resource usage
docker stats

# View container processes
docker-compose top

# Check disk usage
docker system df
```

## Environment Variables

### Set for Docker Compose

Create a `.env` file in the root directory:

```bash
# .env
LANGFLOW_PORT=7860
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

Then reference in docker-compose.yml:

```yaml
ports:
  - "${BACKEND_PORT}:8000"
```

### Set for Development

```bash
# Backend
export LANGFLOW_HOST=localhost
export LANGFLOW_PORT=7860

# Frontend
export VITE_API_URL=http://localhost:8000
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000
lsof -i :3000
lsof -i :7860

# Kill process
kill -9 <PID>

# Or change ports in docker-compose.yml
```

### Container Won't Start

```bash
# Check logs
docker-compose logs <service-name>

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Permission Issues

```bash
# Fix flow directory permissions
sudo chown -R $USER:$USER langflow-backend/flows/

# Or run with sudo (not recommended)
sudo docker-compose up -d
```

## CI/CD Commands (Future)

```bash
# Run tests
npm test          # Frontend
pytest            # Backend

# Build for production
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

## Help and Support

- View API documentation: http://localhost:8000/docs
- Check service status: `docker-compose ps`
- View logs: `docker-compose logs -f`
- GitHub Issues: https://github.com/Stacey77/rag7/issues
