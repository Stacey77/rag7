# 🎸 Ragamuffin

**Ragamuffin** is a full-stack monorepo for building, managing, and executing LangFlow AI agents with a modern web interface.

![Ragamuffin Architecture](https://via.placeholder.com/800x400.png?text=Ragamuffin+AI+Agent+Platform)

## 🚀 Quick Start

```bash
# Start all services (LangFlow, Backend, Frontend)
./start-dev.sh

# Stop all services
./stop-dev.sh
```

## 📦 Services

- **LangFlow** (port 7860): Visual flow builder for creating AI agents
- **FastAPI Backend** (port 8000): REST API for managing and executing flows
- **React Frontend** (port 8080): Modern web UI for interacting with agents

## 📚 Documentation

- [Monorepo Structure](./README_MONOREPO.md) - Detailed architecture overview
- [Run Commands](./RUN_COMMANDS.md) - All available commands and workflows
- [LangFlow Service](./langflow/README.md) - LangFlow container documentation
- [Backend Service](./langflow-backend/README.md) - FastAPI backend documentation
- [Frontend Service](./web-client/README.md) - React web client documentation

## 🛠️ Development

Each service can be developed independently or run together via Docker Compose.

## 📝 License

This project is open source and available under the MIT License.