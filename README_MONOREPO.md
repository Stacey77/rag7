# Epic Platform Monorepo - Detailed Setup Guide

![UI Inspiration](https://i.imgur.com/placeholder-epic-ui.png)

## Architecture Overview

The Epic Platform is a full-stack monorepo designed for building, managing, and executing AI agent workflows. It consists of three main services:

### 1. LangFlow Service (Port 7860)
- Visual workflow builder for creating AI agent flows
- Drag-and-drop interface for connecting components
- Built-in testing and debugging tools
- Export flows as JSON for programmatic execution

### 2. FastAPI Backend (Port 8000)
- Flow management (save, list, retrieve flows)
- Flow execution engine with fallback simulation
- RESTful API for frontend integration
- Persistent storage with volume mounting

### 3. React Frontend (Port 8080)
- Cyberpunk-themed UI with Orbitron font
- Agent Builder page for flow management
- Dashboard for monitoring and analytics
- Playground for testing and experimentation
- Datasets management
- Speech-to-text (STT) and text-to-speech (TTS) conversation interface

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ RAM available for containers
- Ports 7860, 8000, 8080 available

## Installation & Setup

### 1. Clone and Navigate

```bash
git clone https://github.com/Stacey77/rag7.git
cd rag7
```

### 2. Start Services

```bash
# Make scripts executable (first time only)
chmod +x start-dev.sh stop-dev.sh

# Start all services with Docker Compose
./start-dev.sh
```

This will:
- Build all Docker images
- Start LangFlow, Backend, and Frontend services
- Mount persistent volumes for flow storage
- Set up networking between services

### 3. Access Services

Wait for all services to be healthy (check with `docker compose ps`), then access:

- **LangFlow UI**: http://localhost:7860
- **Backend API**: http://localhost:8000 (API docs at http://localhost:8000/docs)
- **Web Client**: http://localhost:8080

### 4. Stop Services

```bash
./stop-dev.sh
```

## Development Workflow

### Creating a Flow

1. Open LangFlow UI at http://localhost:7860
2. Create your agent workflow using visual components
3. Test the flow within LangFlow
4. Export the flow as JSON
5. Upload via Web Client (Agent Builder page) or Backend API

### Running a Flow

#### Via Web Client:
1. Navigate to Agent Builder (http://localhost:8080/agent-builder)
2. Upload or select a saved flow
3. Enter input text
4. Click "Run Flow" to execute

#### Via Backend API:
```bash
curl -X POST http://localhost:8000/run_flow/ \
  -F "flow_file=@myflow.json" \
  -F "user_input=Hello, agent!"
```

### Persistent Storage

Flows are automatically persisted to `./langflow-backend/flows/` on the host machine. This directory is mounted as a volume in the backend container, ensuring flows survive container restarts.

## Service Details

### LangFlow
- **Base Image**: Python 3.11
- **Command**: `langflow run --host 0.0.0.0 --port 7860`
- **Environment**: LANGFLOW_HOST, LANGFLOW_PORT
- **Health Check**: HTTP GET to /health endpoint

### Backend
- **Base Image**: Python 3.11
- **Framework**: FastAPI with Uvicorn
- **Endpoints**:
  - `POST /save_flow/` - Upload and save flow JSON
  - `GET /list_flows/` - List all saved flows
  - `GET /get_flow/{flow_name}` - Retrieve specific flow
  - `POST /run_flow/` - Execute a flow with user input
  - `GET /health` - Health check
- **Fallback Behavior**: If LangFlow is not available, returns simulated responses
- **Volume Mount**: `./langflow-backend/flows` → `/app/flows`

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Server**: Nginx (production)
- **Styling**: Custom cyberpunk theme with Orbitron font
- **Environment**: VITE_API_URL=http://localhost:8000

## Security Considerations

### ⚠️ Current Limitations (Development Only)

1. **No Authentication**: All endpoints are open and unauthenticated
2. **No Authorization**: No role-based access control
3. **Flow Validation**: Uploaded flows are not validated or sandboxed
4. **CORS**: Wide open for localhost development
5. **Flow Storage**: Simple file system storage without versioning
6. **Arbitrary Code Execution**: User flows can execute arbitrary code

### 🔒 Production Recommendations

Before deploying to production:

1. **Authentication & Authorization**
   - Implement JWT or OAuth 2.0
   - Add user management and role-based access
   - Secure all endpoints with authentication middleware

2. **Flow Security**
   - Validate flow JSON schema before execution
   - Sandbox flow execution in isolated containers/workers
   - Implement strict tool and component whitelisting
   - Add flow approval workflow for sensitive operations

3. **Data Storage**
   - Migrate to PostgreSQL or MongoDB with encryption
   - Implement versioning and audit trails
   - Use S3 or similar for large-scale flow storage
   - Add backup and disaster recovery

4. **Network Security**
   - Restrict CORS to production domains only
   - Use HTTPS with valid certificates
   - Implement rate limiting and DDoS protection
   - Add API gateway with request validation

5. **Monitoring & Logging**
   - Add structured logging with log aggregation
   - Implement metrics and alerting (Prometheus, Grafana)
   - Add distributed tracing (OpenTelemetry)
   - Monitor for suspicious flow execution patterns

6. **Container Security**
   - Use non-root users in containers
   - Scan images for vulnerabilities
   - Implement network policies
   - Use secrets management (Vault, AWS Secrets Manager)

## Troubleshooting

### Services Won't Start
```bash
# Check logs
docker compose logs langflow
docker compose logs backend
docker compose logs frontend

# Verify ports are available
netstat -an | grep -E "7860|8000|8080"
```

### Backend Can't Connect to LangFlow
- Ensure LangFlow service is healthy: `docker compose ps`
- Check network connectivity: `docker compose exec backend ping langflow`
- Review backend logs: `docker compose logs backend`

### Frontend Can't Connect to Backend
- Verify backend is running: `curl http://localhost:8000/health`
- Check browser console for CORS errors
- Ensure `.env` has correct VITE_API_URL

### Flow Execution Fails
- Check if LangFlow is installed in backend (see backend logs)
- If using simulation mode, expect mock responses
- Verify flow JSON structure matches LangFlow export format

## Advanced Configuration

### Custom LangFlow Components
Add custom components by extending the LangFlow Dockerfile:
```dockerfile
# In langflow/Dockerfile
COPY ./custom_components /app/custom_components
RUN pip install -e /app/custom_components
```

### Backend Environment Variables
```yaml
# In docker-compose.yml under backend service
environment:
  - LANGFLOW_URL=http://langflow:7860
  - LOG_LEVEL=INFO
  - MAX_FLOW_SIZE_MB=10
  - FLOW_TIMEOUT_SECONDS=300
```

### Frontend Theming
Modify `web-client/src/styles.css` to customize the cyberpunk theme colors, fonts, and animations.

## Next Steps

1. Explore LangFlow and create sample workflows
2. Test the Agent Builder page in the web client
3. Review API documentation at http://localhost:8000/docs
4. Customize the frontend theme and components
5. Plan security hardening for production
6. Add authentication and user management
7. Implement proper flow validation and sandboxing

## Resources

- [LangFlow Documentation](https://docs.langflow.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## Support

For issues, please check the logs first:
```bash
docker compose logs -f
```

For questions or contributions, open an issue on GitHub.
