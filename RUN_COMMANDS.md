# Ragamuffin Run Commands

This guide provides step-by-step instructions for running and developing the Ragamuffin platform.

## 📋 Prerequisites

Before you begin, ensure you have:

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Git**
- At least **4GB of free RAM**
- Ports **7860**, **8000**, and **8080** available

### Verify Prerequisites

```bash
# Check Docker
docker --version
docker-compose --version

# Check available ports
lsof -i :7860
lsof -i :8000
lsof -i :8080
# (Should return nothing if ports are free)
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd rag7
```

### 2. Start All Services

```bash
# Make scripts executable (first time only)
chmod +x start-dev.sh stop-dev.sh

# Start the full stack
./start-dev.sh
```

This command will:
- Build Docker images for all three services
- Start LangFlow, Backend, and Frontend containers
- Set up networking between services
- Mount the flows directory for persistence

**Expected output:**
```
[+] Building ...
[+] Running 4/4
 ✔ Network rag7_ragamuffin-network  Created
 ✔ Container rag7-langflow-1       Started
 ✔ Container rag7-backend-1        Started
 ✔ Container rag7-frontend-1       Started
```

### 3. Wait for Services to Initialize

Services take 30-60 seconds to fully start. You can monitor logs:

```bash
# Watch all logs
docker-compose logs -f

# Watch specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f langflow
```

### 4. Access the Applications

Once services are running:

- **Frontend UI**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **LangFlow Designer**: http://localhost:7860

### 5. Stop All Services

```bash
./stop-dev.sh
```

## 🔧 Development Commands

### Backend Development (FastAPI)

#### Run Backend Locally (Outside Docker)

```bash
cd langflow-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Test Backend Endpoints

```bash
# List flows
curl http://localhost:8000/list_flows/

# Health check
curl http://localhost:8000/

# API docs (in browser)
open http://localhost:8000/docs
```

#### Save a Flow

```bash
curl -X POST http://localhost:8000/save_flow/ \
  -F "file=@my-flow.json"
```

#### Run a Flow

```bash
curl -X POST http://localhost:8000/run_flow/ \
  -F "flow_file=@my-flow.json" \
  -F "user_input=Hello, agent!"
```

### Frontend Development (React + Vite)

#### Run Frontend Locally (Outside Docker)

```bash
cd web-client

# Install dependencies
npm install

# Run development server
npm run dev
# Frontend will be available at http://localhost:5173
```

#### Build Frontend

```bash
cd web-client

# Production build
npm run build

# Preview production build
npm run preview
```

#### Frontend Scripts

```bash
# Lint
npm run lint

# Type check
npm run type-check

# Format code
npm run format
```

### LangFlow Development

#### Access LangFlow UI

Open http://localhost:7860 in your browser to design flows visually.

#### Export Flows

Flows created in LangFlow can be exported as JSON and saved via the backend API.

## 🐳 Docker Commands

### Build Services

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
docker-compose build langflow

# Build without cache (clean build)
docker-compose build --no-cache
```

### Start/Stop Services

```bash
# Start all services
docker-compose up

# Start in detached mode (background)
docker-compose up -d

# Start specific service
docker-compose up backend

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs

# Follow logs (live)
docker-compose logs -f

# Specific service
docker-compose logs backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100
```

### Service Management

```bash
# Restart a service
docker-compose restart backend

# View running services
docker-compose ps

# Execute command in container
docker-compose exec backend bash
docker-compose exec frontend sh
```

### Cleanup

```bash
# Remove stopped containers
docker-compose rm

# Remove all containers, networks, and volumes
docker-compose down -v

# Clean up Docker system
docker system prune -a
```

## 🔍 Troubleshooting

### Port Already in Use

If you get "port already in use" errors:

```bash
# Find process using port
lsof -i :8000
# or
netstat -tuln | grep 8000

# Kill process (replace PID)
kill -9 <PID>
```

Or modify `docker-compose.yml` to use different ports:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Containers Won't Start

```bash
# Check logs for errors
docker-compose logs

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Out of Disk Space

```bash
# Check Docker disk usage
docker system df

# Clean up unused resources
docker system prune -a --volumes
```

### Flow Execution Fails

If `/run_flow/` returns errors:

1. Check backend logs: `docker-compose logs backend`
2. Verify LangFlow is running: `curl http://localhost:7860`
3. If LangFlow is unavailable, the backend will return a simulated response

### Frontend Can't Connect to Backend

1. Verify backend is running: `curl http://localhost:8000`
2. Check CORS settings in `langflow-backend/app/main.py`
3. Verify `.env` file in web-client has correct `VITE_API_URL`

## 📊 Monitoring

### Check Service Health

```bash
# Backend health
curl http://localhost:8000/

# View service status
docker-compose ps

# Check resource usage
docker stats
```

### Inspect Flows Directory

```bash
# List saved flows
ls -la langflow-backend/flows/

# View flow content
cat langflow-backend/flows/my-flow.json
```

## 🧪 Testing

### Test Backend API

```bash
# Using curl
curl -X GET http://localhost:8000/list_flows/

# Using HTTPie (if installed)
http GET http://localhost:8000/list_flows/

# Using Python
python3 -c "import requests; print(requests.get('http://localhost:8000/list_flows/').json())"
```

### Test Frontend

```bash
cd web-client

# Run tests (if configured)
npm test

# E2E tests (if configured)
npm run test:e2e
```

## 🔄 Update and Rebuild

When you make code changes:

```bash
# Backend changes
docker-compose up -d --build backend

# Frontend changes
docker-compose up -d --build frontend

# All changes
docker-compose up -d --build
```

## 📝 Environment Variables

### Backend (.env in langflow-backend/)

```bash
LANGFLOW_URL=http://langflow:7860
LOG_LEVEL=info
```

### Frontend (.env in web-client/)

```bash
VITE_API_URL=http://localhost:8000
```

Modify these before building for different environments.

## 🎯 Common Workflows

### Creating a New Flow

1. Open LangFlow: http://localhost:7860
2. Design your flow visually
3. Export flow as JSON
4. Save via API: `POST /save_flow/`

### Running a Flow

1. Upload flow: `POST /save_flow/`
2. Execute: `POST /run_flow/` with flow file and user input
3. View results in response

### Developing a New Frontend Feature

1. Stop frontend container: `docker-compose stop frontend`
2. Run locally: `cd web-client && npm run dev`
3. Make changes with hot reload
4. Test thoroughly
5. Build and restart: `docker-compose up -d --build frontend`

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vite Documentation](https://vitejs.dev/)
- [LangFlow Documentation](https://docs.langflow.org/)

## ⚠️ Production Deployment

**Do not use these commands for production!**

For production:
1. Use environment-specific compose files
2. Set up proper secrets management
3. Configure SSL/TLS
4. Implement authentication
5. Set up monitoring and logging
6. Use a reverse proxy (nginx, traefik)
7. Configure resource limits
8. Set up backups for flows directory

---

For issues or questions, please refer to the project README or open an issue.
