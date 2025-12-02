# Epic Platform - RAG7 Monorepo

Welcome to the Epic Platform monorepo! This project provides a comprehensive platform for building and deploying AI agents using LangFlow, FastAPI, and React.

## UI Preview

![Epic Platform UI](https://raw.githubusercontent.com/Stacey77/rag7/main/docs/ui-preview.png)

## Quick Start

```bash
# Start all services
./start-dev.sh

# Stop all services
./stop-dev.sh
```

## Services

- **LangFlow**: Visual flow builder for AI agents (http://localhost:7860)
- **Backend API**: FastAPI service for flow management (http://localhost:8000)
- **Web Client**: React frontend for managing flows (http://localhost:3000)

## Documentation

- [Monorepo Documentation](./README_MONOREPO.md) - Detailed architecture and setup
- [Run Commands](./RUN_COMMANDS.md) - All available commands and operations
- [LangFlow Usage](./langflow/README.md) - LangFlow container details
- [Backend API](./langflow-backend/README.md) - API endpoints and usage

## Project Structure

```
rag7/
├── langflow/              # LangFlow container
├── langflow-backend/      # FastAPI backend service
├── web-client/            # React + TypeScript frontend
├── docker-compose.yml     # Docker orchestration
└── start-dev.sh           # Development startup script
```

## Next Steps

After initial setup:
1. Secure CORS configuration for production
2. Add authentication and authorization
3. Implement flow validation
4. Configure persistent storage
5. Add monitoring and logging

## Contributing

Please see individual service READMEs for development guidelines.