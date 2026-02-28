# Ragamuffin Monorepo

<img src="https://via.placeholder.com/800x400?text=Ragamuffin+UI+Inspiration" alt="Ragamuffin UI Inspiration" />

## Overview

**Ragamuffin** is a full-stack AI development platform that combines:

- **LangFlow** (port 7860): Visual flow-based LLM application builder
- **FastAPI Backend** (port 8000): API layer for flow management and execution
- **React Frontend** (port 8080): Cyberpunk-themed web client with dashboard, playground, and agent builder
- **LangGraph** (port 7878): Graph-based agent orchestration

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Docker Compose                          │
├─────────────┬─────────────┬─────────────┬─────────────────────────┤
│  LangFlow   │   Backend   │  Frontend   │       LangGraph        │
│   :7860     │    :8000    │   :8080     │         :7878          │
└─────────────┴─────────────┴─────────────┴─────────────────────────┘
```

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Stacey77/rag7.git
   cd rag7
   ```

2. **Start all services**
   ```bash
   ./start-dev.sh
   # or
   docker compose up --build
   ```

3. **Access the services**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8000
   - LangFlow UI: http://localhost:7860
   - LangGraph: http://localhost:7878

4. **Stop all services**
   ```bash
   ./stop-dev.sh
   # or
   docker compose down
   ```

## Project Structure

```
ragamuffin/
├── docker-compose.yml          # Orchestrates all services
├── langflow/                   # LangFlow visual builder
│   ├── Dockerfile
│   └── README.md
├── langflow-backend/           # FastAPI backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── flows/                  # Persisted flow files
│   └── app/
│       ├── __init__.py
│       └── main.py
├── web-client/                 # React frontend
│   ├── Dockerfile
│   ├── package.json
│   └── src/
└── langgraph/                  # LangGraph server
    ├── Dockerfile
    └── README.md
```

## Security Considerations

⚠️ **Important**: Before deploying to production:

- **Validate flows**: Always validate flow JSON before execution
- **Sandbox executions**: Run flows in isolated environments
- **Whitelist tools**: Only allow approved tools/functions
- **Add authentication**: Implement JWT/OAuth for API access
- **Secure CORS**: Restrict origins in production
- **Persistent storage**: Use a database or S3 for flow storage

## Development

See [RUN_COMMANDS.md](./RUN_COMMANDS.md) for detailed development commands.

## License

MIT
