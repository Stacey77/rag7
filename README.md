# Epic Platform - RAG7 Monorepo

A comprehensive monorepo scaffold for building and executing visual AI agent workflows using LangFlow, FastAPI, and React.

![Epic Platform UI Inspiration](https://i.imgur.com/placeholder-epic-ui.png)

## Overview

This monorepo provides a complete development environment for creating AI agent workflows with:

- **LangFlow UI** (port 7860): Visual workflow builder for creating AI agent flows
- **FastAPI Backend** (port 8000): API server for managing and executing flows
- **React Frontend** (port 8080): Cyberpunk-themed web interface with STT/TTS capabilities

## Quick Start

```bash
# Start all services
./start-dev.sh

# Stop all services
./stop-dev.sh
```

## Services

- **LangFlow**: http://localhost:7860 - Visual workflow editor
- **Backend API**: http://localhost:8000 - FastAPI server with flow management
- **Web Client**: http://localhost:8080 - React frontend application

## Project Structure

```
.
├── docker-compose.yml          # Multi-service orchestration
├── langflow/                   # LangFlow service
├── langflow-backend/           # FastAPI backend
│   ├── flows/                  # Persisted flow storage
│   └── app/                    # FastAPI application
└── web-client/                 # React frontend
    └── src/
        ├── components/         # UI components
        └── pages/              # Application pages
```

## Documentation

- [Monorepo Setup](./README_MONOREPO.md) - Detailed architecture and setup
- [Run Commands](./RUN_COMMANDS.md) - All available commands
- [LangFlow Service](./langflow/README.md) - LangFlow configuration
- [Backend API](./langflow-backend/README.md) - Backend endpoints and usage
- [Web Client](./web-client/README.md) - Frontend development

## Security Considerations

⚠️ **This is a development scaffold with NO authentication or authorization.**

Before production deployment:
1. Add JWT/OAuth authentication
2. Implement flow validation and sandboxing
3. Add CORS restrictions for production domains
4. Move flow storage to a database or S3 with versioning
5. Implement proper access controls and audit logging
6. Sandbox flow execution in isolated containers

## Features

- Visual agent workflow building with LangFlow
- Flow persistence and version management
- RESTful API for flow operations
- Modern React UI with cyberpunk theme
- Speech-to-text and text-to-speech capabilities
- Docker Compose orchestration

## Development

See [RUN_COMMANDS.md](./RUN_COMMANDS.md) for detailed development commands and workflows.

## License

MIT