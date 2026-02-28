# Ragamuffin - rag7

<img src="https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800&auto=format&fit=crop&q=60" alt="Ragamuffin UI" width="600">

**Ragamuffin** is a visual LangFlow agent building and execution platform powered by FastAPI and React.

## Quick Start

```bash
# Start all services (LangFlow, Backend, Frontend)
./start-dev.sh

# Stop all services
./stop-dev.sh
```

Access the services:
- **LangFlow**: http://localhost:7860
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:8080

## Documentation

- [Monorepo Overview](./README_MONOREPO.md) - Complete architecture and setup guide
- [Run Commands](./RUN_COMMANDS.md) - Detailed development and deployment commands

## What's Included

- **LangFlow Service**: Visual workflow builder for AI agents
- **FastAPI Backend**: RESTful API for flow management and execution
- **React Frontend**: Modern UI with cyberpunk aesthetics (Vite + TypeScript)
- **Docker Compose**: Complete containerized development environment

## Architecture

```
├── langflow/              # LangFlow service
├── langflow-backend/      # FastAPI backend + flow persistence
└── web-client/           # React frontend (Vite + TypeScript)
```

## Next Steps

1. Start the services with `./start-dev.sh`
2. Visit LangFlow at http://localhost:7860 to create workflows
3. Use the Frontend at http://localhost:8080 to manage and run agents
4. Check [README_MONOREPO.md](./README_MONOREPO.md) for detailed documentation

For production deployment, see security and configuration notes in [README_MONOREPO.md](./README_MONOREPO.md).