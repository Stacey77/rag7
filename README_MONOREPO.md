# Ragamuffin Monorepo

<img src="https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800&auto=format&fit=crop&q=60" alt="Ragamuffin UI Inspiration" width="600">

## Overview

**Ragamuffin** is a powerful monorepo scaffold that enables visual LangFlow agent building and execution through a modern web interface. The project combines:

- **LangFlow**: Visual agent/workflow builder running on port 7860
- **FastAPI Backend**: RESTful API for flow management and execution on port 8000
- **React Frontend**: Modern Vite+React+TypeScript UI with cyberpunk aesthetics on port 8080

The architecture allows you to visually design AI agent workflows in LangFlow, save and manage them through the backend API, and interact with them through a beautiful web interface.

## Architecture

```
Ragamuffin Monorepo
├── langflow/              # LangFlow service container
├── langflow-backend/      # FastAPI backend with flow persistence
│   └── flows/            # Persisted flow JSON files (mounted volume)
└── web-client/           # Vite + React + TypeScript frontend
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Ports 7860, 8000, and 8080 available

### Start the Development Environment

```bash
# Make scripts executable (first time only)
chmod +x start-dev.sh stop-dev.sh

# Start all services
./start-dev.sh
```

This will:
1. Build all Docker images
2. Start LangFlow on http://localhost:7860
3. Start the Backend API on http://localhost:8000
4. Start the Frontend on http://localhost:8080

### Stop the Development Environment

```bash
./stop-dev.sh
```

## Services

### LangFlow (Port 7860)
Visual workflow builder for creating AI agent flows. Access the LangFlow UI to design and test your agents.

### Backend API (Port 8000)
FastAPI service providing endpoints for:
- Saving flows (POST /save_flow/)
- Listing flows (GET /list_flows/)
- Getting flow details (GET /get_flow/{flow_name})
- Running flows (POST /run_flow/)

API Documentation: http://localhost:8000/docs

### Frontend (Port 8080)
React-based web application featuring:
- Dashboard for monitoring agents
- Playground for testing interactions
- Agent Builder integrated with backend
- Datasets management
- Cyberpunk-themed UI with Orbitron font

## Flow Persistence

Flow files are stored in `./langflow-backend/flows/` and persisted across container restarts. This directory is mounted as a volume in the backend container.

## Project Structure

See individual README files in each service directory for more details:
- [LangFlow Service](/langflow/README.md)
- [Backend Service](/langflow-backend/README.md)
- [Web Client](/web-client/README.md)

## Development

For detailed development commands and workflows, see [RUN_COMMANDS.md](./RUN_COMMANDS.md).

## Security Notes

⚠️ **Important**: This is a development scaffold. Before deploying to production:

1. Configure CORS properly (currently set for localhost development)
2. Add authentication and authorization
3. Implement flow validation and sandboxing
4. Use persistent database instead of SQLite
5. Add rate limiting and input validation
6. Secure all API endpoints
7. Use environment variables for sensitive configuration
8. Implement proper logging and monitoring

## Next Steps

1. **Secure CORS**: Update backend CORS settings for production domains
2. **Validate Flows**: Add schema validation for uploaded flows
3. **Add Authentication**: Implement user authentication and authorization
4. **Persistent Storage**: Configure production-grade database
5. **Monitoring**: Add logging, metrics, and health checks
6. **CI/CD**: Set up automated testing and deployment pipelines

## Contributing

This scaffold is designed to be extended. Key areas for enhancement:
- Additional backend endpoints
- Enhanced UI components
- Integration with more AI services
- Advanced flow management features
- User management and permissions

## License

See repository root for license information.
