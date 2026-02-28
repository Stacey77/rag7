# Epic Platform Monorepo

This monorepo contains a full-stack AI platform built with LangFlow, FastAPI, and React.

## Architecture

```
epic-platform/
├── langflow/           # LangFlow service for visual flow building
├── langflow-backend/   # FastAPI backend for flow management
├── web-client/         # React/TypeScript frontend
└── docker-compose.yml  # Orchestration configuration
```

## Services

### LangFlow (Port 7860)
Visual flow builder for creating AI workflows. Access at `http://localhost:7860`

### Backend API (Port 8000)
FastAPI service providing flow management endpoints:
- `POST /save_flow/` - Save a LangFlow definition
- `GET /list_flows/` - List all saved flows
- `GET /get_flow/{flow_name}` - Retrieve a specific flow
- `POST /run_flow/` - Execute a flow with user input

API docs available at `http://localhost:8000/docs`

### Web Client (Port 8080)
React-based UI with cyberpunk theme featuring:
- Dashboard with metrics and visualization
- Playground for testing flows
- Dataset management
- Agent Builder for flow creation/editing
- Real-time conversation interface with STT/TTS

Access at `http://localhost:8080`

## Quick Start

See [RUN_COMMANDS.md](./RUN_COMMANDS.md) for detailed instructions.

```bash
# Start all services
./start-dev.sh

# Stop all services
./stop-dev.sh
```

## Development

Each service can be developed independently:
- See `langflow/README.md` for LangFlow details
- See `langflow-backend/README.md` for backend development
- See `web-client/README.md` for frontend development

## Data Persistence

- LangFlow data: Docker volume `langflow-data`
- Saved flows: `./langflow-backend/flows` (mounted volume)

## Network

All services communicate via the `rag7-network` bridge network.

## Next Steps

1. **Security**: Configure production CORS settings
2. **Validation**: Add flow schema validation
3. **Authentication**: Implement user auth and API keys
4. **Storage**: Add database for persistent storage
5. **Monitoring**: Add logging and metrics collection
