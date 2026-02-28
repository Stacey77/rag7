# Ragamuffin Monorepo

![Ragamuffin UI Concept](https://via.placeholder.com/800x400/1a1a2e/16c2d5?text=Ragamuffin+Visual+Agent+Builder)

**Ragamuffin** is a comprehensive monorepo scaffold that enables visual LangFlow agent building and execution. It combines the power of LangFlow's visual programming interface with a FastAPI backend and a modern React+TypeScript frontend featuring a cyberpunk-inspired design.

## Architecture

The monorepo consists of three main services:

1. **LangFlow Service** (Port 7860) - Visual agent building interface
2. **FastAPI Backend** (Port 8000) - Flow management and execution API
3. **React Frontend** (Port 8080) - Modern web interface with cyberpunk theme

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Running the Application

1. Clone the repository:
```bash
git clone <repository-url>
cd rag7
```

2. Start all services:
```bash
./start-dev.sh
```

This will build and start all three services:
- LangFlow UI: http://localhost:7860
- Backend API: http://localhost:8000
- Frontend UI: http://localhost:8080

3. Stop all services:
```bash
./stop-dev.sh
```

## Project Structure

```
.
├── docker-compose.yml          # Orchestrates all services
├── start-dev.sh                # Quick start script
├── stop-dev.sh                 # Quick stop script
├── langflow/                   # LangFlow service
│   ├── Dockerfile
│   └── README.md
├── langflow-backend/           # FastAPI backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── flows/                  # Persisted flows (mounted volume)
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   └── README.md
└── web-client/                 # React+TypeScript frontend
    ├── Dockerfile
    ├── package.json
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   └── ...
    └── README.md
```

## Features

### Visual Agent Building
- Drag-and-drop interface via LangFlow
- Visual flow creation and editing
- Real-time flow testing

### Backend API
- **POST /save_flow/** - Save flow definitions
- **GET /list_flows/** - List all saved flows
- **GET /get_flow/{flow_name}** - Retrieve specific flow
- **POST /run_flow/** - Execute a flow with user input

### Frontend
- Cyberpunk-themed UI with Orbitron font
- Dashboard for monitoring agents
- Agent Builder integration
- Playground for testing
- Dataset management
- STT/TTS conversation interface

## Flow Persistence

Flows are persisted in `./langflow-backend/flows/` directory, which is mounted as a volume in the backend container. This ensures your flows survive container restarts.

## Security Considerations

⚠️ **IMPORTANT SECURITY WARNINGS** ⚠️

This scaffold is designed for **development and prototyping only**. Before deploying to production:

1. **Authentication & Authorization**
   - Implement JWT or OAuth authentication
   - Add role-based access control
   - Secure all API endpoints

2. **Flow Validation**
   - Validate flow definitions before execution
   - Sanitize all user inputs
   - Implement flow schema validation

3. **Sandboxing**
   - Run flows in isolated containers or workers
   - Implement resource limits (CPU, memory, time)
   - Restrict network access for flow execution

4. **Tool Restrictions**
   - Whitelist allowed LangFlow components
   - Restrict file system access
   - Limit external API calls

5. **Data Storage**
   - Move from file-based storage to database (PostgreSQL, MongoDB)
   - Consider cloud storage (S3, GCS) for scalability
   - Implement encryption at rest

6. **CORS Configuration**
   - Restrict CORS to specific domains
   - Remove localhost origins in production
   - Implement proper CSRF protection

## Development

See [RUN_COMMANDS.md](RUN_COMMANDS.md) for detailed development commands and workflows.

## Next Steps

1. Configure environment-specific settings
2. Implement authentication layer
3. Add database integration
4. Set up CI/CD pipelines
5. Implement monitoring and logging
6. Add comprehensive testing
7. Security audit and hardening

## Contributing

This is a scaffold project. Feel free to extend and customize based on your requirements.

## License

[Add your license here]
