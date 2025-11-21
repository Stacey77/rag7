# Ragamuffin Platform

![Ragamuffin UI Inspiration](<img>)

**Ragamuffin** is an advanced AI orchestration platform that combines LangFlow for visual flow design, a FastAPI backend for flow management and execution, and a modern React + TypeScript web interface with a cyberpunk-inspired design.

## Project Name
**Ragamuffin** - A powerful monorepo platform for building, managing, and deploying AI agent workflows.

## Architecture Overview
This monorepo contains three main components:
- **LangFlow Container**: Visual AI flow designer (port 7860)
- **FastAPI Backend**: Flow persistence and execution API (port 8000)
- **Web Client**: React + TypeScript frontend with Vite (port 8080)

## Quick Start
```bash
# Start all services
./start-dev.sh

# Stop all services
./stop-dev.sh
```

## Access Points
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **LangFlow UI**: http://localhost:7860

## Documentation
- See [README_MONOREPO.md](./README_MONOREPO.md) for detailed monorepo structure
- See [RUN_COMMANDS.md](./RUN_COMMANDS.md) for comprehensive run instructions
- Individual service READMEs in each service directory

## UI Inspiration
The web client features a cyberpunk-inspired design with the Orbitron font and modern React components:

![UI Reference](<img>)

## Next Steps
After setup, consider:
- Implementing authentication and authorization
- Securing CORS for production
- Adding flow validation and sandboxing
- Setting up persistent storage for flows
- Implementing user management