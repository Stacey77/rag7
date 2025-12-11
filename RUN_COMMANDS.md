# Ragamuffin - Run Commands

This document provides step-by-step instructions for running and developing the Ragamuffin monorepo.

## Prerequisites

Ensure you have the following installed:
- Docker (version 20.10 or higher)
- Docker Compose (version 1.29 or higher)
- Git

## Quick Start Commands

### Start All Services

```bash
# Make scripts executable (first time only)
chmod +x start-dev.sh stop-dev.sh

# Start all services with build
./start-dev.sh
```

This command will:
1. Build Docker images for all services
2. Start LangFlow (port 7860)
3. Start Backend API (port 8000)
4. Start Frontend (port 8080)

### Stop All Services

```bash
./stop-dev.sh
```

This command will gracefully stop all running containers.

## Manual Docker Compose Commands

### Build and Start

```bash
# Build all images
docker compose build

# Start all services
docker compose up

# Build and start in one command
docker compose up --build

# Start in detached mode (background)
docker compose up -d --build
```

### Stop Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# Stop and remove images
docker compose down --rmi all
```

### View Logs

```bash
# View logs for all services
docker compose logs

# View logs for specific service
docker compose logs langflow
docker compose logs backend
docker compose logs frontend

# Follow logs in real-time
docker compose logs -f

# Follow logs for specific service
docker compose logs -f backend
```

### Restart Services

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart backend
```

## Development Workflow

### 1. Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd rag7

# Make scripts executable
chmod +x start-dev.sh stop-dev.sh

# Start services
./start-dev.sh
```

### 2. Access Services

Once all services are running:

- **LangFlow UI**: http://localhost:7860
  - Create and edit visual flows
  
- **Backend API**: http://localhost:8000
  - API documentation: http://localhost:8000/docs
  - Alternative docs: http://localhost:8000/redoc
  
- **Frontend UI**: http://localhost:8080
  - Main application interface

### 3. Making Changes

#### Backend Changes

```bash
# After modifying backend code
docker compose up -d --build backend

# View backend logs
docker compose logs -f backend
```

#### Frontend Changes

```bash
# After modifying frontend code
docker compose up -d --build frontend

# View frontend logs
docker compose logs -f frontend
```

#### LangFlow Changes

```bash
# After modifying LangFlow configuration
docker compose up -d --build langflow

# View LangFlow logs
docker compose logs -f langflow
```

### 4. Testing API Endpoints

```bash
# List all flows
curl http://localhost:8000/list_flows/

# Get specific flow
curl http://localhost:8000/get_flow/my_flow_name

# Save a flow (example)
curl -X POST http://localhost:8000/save_flow/ \
  -F "flow_file=@path/to/flow.json"

# Run a flow (example)
curl -X POST http://localhost:8000/run_flow/ \
  -F "flow_file=@path/to/flow.json" \
  -F "user_input=Hello, world!"
```

### 5. Debugging

```bash
# Check service status
docker compose ps

# Inspect a container
docker compose exec backend bash

# View container resource usage
docker stats

# Check network connectivity
docker compose exec backend ping langflow
```

## Local Development Without Docker

### Backend Development

```bash
cd langflow-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd web-client

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
lsof -i :7860  # or :8000, :8080

# Kill the process
kill -9 <PID>

# Or use different ports in docker-compose.yml
```

### Container Fails to Start

```bash
# View detailed logs
docker compose logs <service-name>

# Remove all containers and volumes
docker compose down -v

# Rebuild from scratch
docker compose up --build --force-recreate
```

### Changes Not Reflecting

```bash
# Clear Docker build cache
docker compose build --no-cache

# Restart with fresh build
docker compose down && docker compose up --build
```

### Volume Permission Issues

```bash
# On Linux, ensure proper permissions for flows directory
sudo chown -R $USER:$USER langflow-backend/flows

# Or run with appropriate user in docker-compose.yml
```

## Production Deployment

⚠️ **Security Warning**: This setup is for development only.

For production deployment:

1. **Environment Configuration**
   - Use environment-specific configuration files
   - Store secrets in environment variables or secret management services
   - Configure proper CORS origins

2. **Security Hardening**
   - Implement authentication and authorization
   - Use HTTPS with valid certificates
   - Enable rate limiting
   - Implement input validation and sanitization

3. **Scalability**
   - Use orchestration platforms (Kubernetes, Docker Swarm)
   - Implement load balancing
   - Use managed databases
   - Configure auto-scaling

4. **Monitoring**
   - Set up logging aggregation
   - Implement metrics collection
   - Configure alerting
   - Health checks

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [LangFlow Documentation](https://docs.langflow.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)

## Support

For issues or questions, please refer to the main README.md or create an issue in the repository.
