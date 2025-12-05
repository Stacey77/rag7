# Run Commands Reference

This document provides a comprehensive list of commands for working with the Epic Platform monorepo.

## Quick Start Commands

```bash
# Start all services (builds images if needed)
./start-dev.sh

# Stop all services
./stop-dev.sh
```

## Docker Compose Commands

### Service Management

```bash
# Build all images
docker compose build

# Build specific service
docker compose build langflow
docker compose build backend
docker compose build frontend

# Start all services
docker compose up

# Start all services with rebuild
docker compose up --build

# Start in detached mode (background)
docker compose up -d

# Start specific service
docker compose up langflow

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# View running services
docker compose ps

# View service logs
docker compose logs

# Follow logs in real-time
docker compose logs -f

# View logs for specific service
docker compose logs langflow
docker compose logs backend
docker compose logs frontend

# Restart a service
docker compose restart backend
```

### Container Access

```bash
# Execute command in running container
docker compose exec backend bash
docker compose exec langflow bash
docker compose exec frontend sh

# View container stats
docker compose stats

# Inspect service configuration
docker compose config
```

## Development Commands

### Backend (FastAPI)

```bash
# Access backend container
docker compose exec backend bash

# Inside container - view logs
tail -f /var/log/backend.log

# Test backend endpoint
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# List saved flows
curl http://localhost:8000/list_flows/

# Save a flow
curl -X POST http://localhost:8000/save_flow/ \
  -F "flow=@path/to/flow.json"

# Run a flow
curl -X POST http://localhost:8000/run_flow/ \
  -F "flow_file=@path/to/flow.json" \
  -F "user_input=Your input here"

# Get specific flow
curl http://localhost:8000/get_flow/myflow.json
```

### Frontend (React)

```bash
# Access frontend container
docker compose exec frontend sh

# Local development (outside Docker)
cd web-client
npm install
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

### LangFlow

```bash
# Access LangFlow UI
open http://localhost:7860

# Access LangFlow container
docker compose exec langflow bash

# View LangFlow logs
docker compose logs -f langflow
```

## File Management

### Flow Persistence

```bash
# View saved flows
ls -la langflow-backend/flows/

# Backup flows
tar -czf flows-backup-$(date +%Y%m%d).tar.gz langflow-backend/flows/

# Restore flows
tar -xzf flows-backup-20231115.tar.gz

# Clear all flows (careful!)
rm langflow-backend/flows/*.json
```

### Volume Management

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect rag7_langflow-flows

# Remove unused volumes
docker volume prune
```

## Testing Commands

### Health Checks

```bash
# Check all services are healthy
docker compose ps

# Test LangFlow
curl http://localhost:7860/health

# Test Backend
curl http://localhost:8000/health

# Test Frontend
curl http://localhost:8080
```

### End-to-End Testing

```bash
# 1. Create a simple flow in LangFlow UI
open http://localhost:7860

# 2. Export and save flow
curl -X POST http://localhost:8000/save_flow/ \
  -F "flow=@test-flow.json"

# 3. List flows to verify
curl http://localhost:8000/list_flows/

# 4. Run the flow
curl -X POST http://localhost:8000/run_flow/ \
  -F "flow_file=@test-flow.json" \
  -F "user_input=Test message"

# 5. Test via web UI
open http://localhost:8080/agent-builder
```

## Debugging Commands

### View Logs

```bash
# All services
docker compose logs -f

# Specific service with timestamps
docker compose logs -f --timestamps backend

# Last 100 lines
docker compose logs --tail=100 backend

# Since specific time
docker compose logs --since 2023-11-15T10:00:00 backend
```

### Network Debugging

```bash
# Check service connectivity
docker compose exec backend ping langflow
docker compose exec frontend ping backend

# View network details
docker network inspect rag7_epic-platform

# Test ports from host
nc -zv localhost 7860
nc -zv localhost 8000
nc -zv localhost 8080
```

### Resource Usage

```bash
# View container resource usage
docker compose stats

# View disk usage
docker system df

# View detailed system info
docker system info
```

## Cleanup Commands

### Soft Cleanup

```bash
# Stop services but keep volumes
docker compose down

# Stop and remove anonymous volumes
docker compose down --volumes
```

### Hard Cleanup

```bash
# Stop and remove everything
docker compose down -v --remove-orphans

# Remove all unused containers, networks, images
docker system prune -a

# Remove only unused volumes
docker volume prune

# Complete cleanup (DESTRUCTIVE - removes all flows)
docker compose down -v
rm -rf langflow-backend/flows/*
docker system prune -a -f
```

## Maintenance Commands

### Update Dependencies

```bash
# Rebuild with latest base images
docker compose build --no-cache

# Pull latest base images
docker compose pull

# Update backend Python packages
cd langflow-backend
docker compose exec backend pip install --upgrade -r requirements.txt

# Update frontend packages
cd web-client
npm update
```

### Backup & Restore

```bash
# Backup entire setup
tar -czf epic-platform-backup-$(date +%Y%m%d).tar.gz \
  docker-compose.yml \
  langflow/ \
  langflow-backend/ \
  web-client/

# Restore
tar -xzf epic-platform-backup-20231115.tar.gz
./start-dev.sh
```

## Production Deployment

### Build for Production

```bash
# Build all production images
docker compose -f docker-compose.prod.yml build

# Push to registry (after setting up registry)
docker compose -f docker-compose.prod.yml push

# Deploy to production
docker compose -f docker-compose.prod.yml up -d
```

### Environment Configuration

```bash
# Set environment variables for production
export LANGFLOW_URL=https://langflow.example.com
export BACKEND_URL=https://api.example.com
export FRONTEND_URL=https://app.example.com

# Or use .env file
cat > .env.production << EOF
LANGFLOW_URL=https://langflow.example.com
BACKEND_URL=https://api.example.com
FRONTEND_URL=https://app.example.com
EOF
```

## Troubleshooting Commands

### Port Conflicts

```bash
# Find process using port 8000
lsof -i :8000
netstat -an | grep 8000

# Kill process using port
kill -9 $(lsof -t -i:8000)
```

### Permission Issues

```bash
# Fix flow directory permissions
sudo chown -R $USER:$USER langflow-backend/flows
chmod -R 755 langflow-backend/flows

# Fix script permissions
chmod +x start-dev.sh stop-dev.sh
```

### Container Issues

```bash
# Force recreate containers
docker compose up --force-recreate

# Remove and rebuild
docker compose rm -f backend
docker compose build backend
docker compose up backend

# Clear Docker cache completely
docker builder prune -a -f
```

## Utility Scripts

### Create Test Flow

```bash
# Create a simple test flow
cat > test-flow.json << EOF
{
  "name": "test-flow",
  "description": "Simple test flow",
  "nodes": []
}
EOF

curl -X POST http://localhost:8000/save_flow/ \
  -F "flow=@test-flow.json"
```

### Monitor Resources

```bash
# Continuous monitoring
watch -n 2 'docker compose ps && docker compose stats --no-stream'
```

### Quick Reset

```bash
# Reset everything to clean state
./stop-dev.sh
docker compose down -v
rm -rf langflow-backend/flows/*.json
./start-dev.sh
```

## Help & Documentation

```bash
# Docker Compose help
docker compose --help

# Service-specific help
docker compose run backend --help

# View Swagger API docs
open http://localhost:8000/docs

# View ReDoc API docs
open http://localhost:8000/redoc
```

## Performance Optimization

```bash
# Limit container resources
docker compose up --scale backend=2

# View resource limits
docker compose config

# Prune unused data to free space
docker system prune -a --volumes -f
```

## Common Workflows

### Daily Development

```bash
# Morning startup
./start-dev.sh
open http://localhost:8080

# Check status
docker compose ps

# Evening shutdown
./stop-dev.sh
```

### Feature Development

```bash
# Start services
./start-dev.sh

# Make changes to code
# (Backend/Frontend auto-reload in dev mode)

# View logs
docker compose logs -f backend

# Test changes
curl http://localhost:8000/health

# Commit when ready
git add .
git commit -m "feat: add new feature"
```

### Debugging Issues

```bash
# Check all services
docker compose ps

# View problematic service logs
docker compose logs backend

# Restart problematic service
docker compose restart backend

# If needed, rebuild
docker compose up --build backend

# Access container for investigation
docker compose exec backend bash
```

## Additional Resources

- Docker Compose: https://docs.docker.com/compose/
- FastAPI: https://fastapi.tiangolo.com/
- LangFlow: https://docs.langflow.org/
- React + Vite: https://vitejs.dev/guide/
