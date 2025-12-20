# Epic Platform Monorepo Documentation

## Overview

This monorepo contains a complete platform for building, managing, and deploying AI agents using LangFlow for visual flow building, FastAPI for backend services, and React for the web interface.

## UI Inspiration

<img src="https://raw.githubusercontent.com/Stacey77/rag7/main/docs/ui-preview.png" alt="Epic Platform Interface" />

## Architecture

### Components

1. **LangFlow Container** (`/langflow`)
   - Visual flow builder for AI agents
   - Runs on port 7860
   - Provides drag-and-drop interface for creating AI workflows

2. **FastAPI Backend** (`/langflow-backend`)
   - RESTful API for flow management
   - Endpoints for save, list, get, and run flows
   - Integrates with LangFlow engine
   - Runs on port 8000

3. **React Web Client** (`/web-client`)
   - Modern UI built with Vite + React + TypeScript
   - Dashboard for flow management
   - Agent builder interface
   - Playground for testing agents
   - Runs on port 3000

### Data Flow

```
User → React Web Client → FastAPI Backend → LangFlow Engine
                              ↓
                      Flow Storage (JSON)
```

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Git
- (Optional) Node.js 18+ for local frontend development
- (Optional) Python 3.9+ for local backend development

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Stacey77/rag7.git
cd rag7

# Start all services
./start-dev.sh

# Access services
# - LangFlow: http://localhost:7860
# - Backend API: http://localhost:8000
# - Web Client: http://localhost:3000
# - API Docs: http://localhost:8000/docs
```

### Manual Setup

```bash
# Build and start all containers
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## Service Details

### LangFlow

- **Purpose**: Visual AI flow builder
- **Technology**: Python-based web application
- **Port**: 7860
- **Volume**: `langflow_data` for persistent storage

### Backend API

- **Purpose**: Flow management and execution
- **Technology**: FastAPI (Python)
- **Port**: 8000
- **Endpoints**:
  - `POST /save_flow/` - Save a LangFlow JSON
  - `GET /list_flows/` - List all saved flows
  - `GET /get_flow/{flow_name}` - Retrieve a specific flow
  - `POST /run_flow/` - Execute a flow with input data
- **Volume**: `./langflow-backend/flows` for flow storage

### Web Client

- **Purpose**: User interface for flow management
- **Technology**: React + TypeScript + Vite
- **Port**: 3000
- **Features**:
  - Dashboard with flow overview
  - Agent builder interface
  - Playground for testing
  - Dataset management

## Configuration

### Environment Variables

**Backend** (`langflow-backend`):
- `LANGFLOW_HOST`: Hostname of LangFlow service (default: langflow)
- `LANGFLOW_PORT`: Port of LangFlow service (default: 7860)

**Web Client**:
- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)

### CORS Configuration

The backend is configured with permissive CORS for development. For production:

```python
# Update in langflow-backend/app/main.py
origins = [
    "https://yourdomain.com",
    # Add production domains
]
```

## Storage

### Flow Persistence

Flows are stored as JSON files in the `langflow-backend/flows` directory, which is mounted as a volume. This ensures flows persist across container restarts.

### LangFlow Data

LangFlow's internal data (database, settings) is stored in the `langflow_data` Docker volume.

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development Workflow

### Adding a New Flow

1. Open LangFlow at http://localhost:7860
2. Design your flow visually
3. Export the flow JSON
4. Save via the web client or API
5. Run the flow through the API

### Local Development (Without Docker)

**Backend**:
```bash
cd langflow-backend
pip install -r app/requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**:
```bash
cd web-client
npm install
npm run dev
```

## Testing

### Backend
```bash
cd langflow-backend
pytest  # Add tests in tests/ directory
```

### Frontend
```bash
cd web-client
npm test
```

## Security Considerations

⚠️ **Important for Production**:

1. **CORS**: Restrict allowed origins to specific domains
2. **Authentication**: Add user authentication (JWT, OAuth)
3. **Flow Validation**: Validate and sanitize flow JSON before execution
4. **Rate Limiting**: Implement rate limiting on API endpoints
5. **Secrets Management**: Use proper secret management (not .env files)
6. **HTTPS**: Enable TLS/SSL for all services
7. **Input Validation**: Sanitize all user inputs
8. **Network Security**: Use proper network isolation and firewalls

## Troubleshooting

### Container Issues

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f [service_name]

# Restart a service
docker-compose restart [service_name]

# Clean rebuild
docker-compose down -v
docker-compose up --build
```

### Port Conflicts

If ports are already in use, modify the port mappings in `docker-compose.yml`:

```yaml
ports:
  - "8080:7860"  # LangFlow
  - "8001:8000"  # Backend
  - "3001:80"    # Web Client
```

## Recommended Next Steps

1. **Add Authentication**
   - Implement JWT-based auth in backend
   - Add login/logout to web client
   - Protect sensitive endpoints

2. **Flow Validation**
   - Add schema validation for flow JSON
   - Implement security checks before execution
   - Add flow versioning

3. **Persistent Storage**
   - Configure proper database (PostgreSQL)
   - Add backup and restore functionality
   - Implement data migration scripts

4. **Monitoring**
   - Add logging aggregation (ELK stack)
   - Implement metrics collection (Prometheus)
   - Set up alerting

5. **CI/CD**
   - Add automated testing
   - Set up deployment pipelines
   - Implement staging environments

## Resources

- [LangFlow Documentation](https://docs.langflow.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)

## Support

For issues and questions, please open a GitHub issue in the repository.
