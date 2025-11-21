# Ragamuffin 🤖

![Ragamuffin UI](https://via.placeholder.com/800x400/1a1a2e/16f4d0?text=Ragamuffin+AI+Agent+Builder)

**Ragamuffin** is a visual AI agent building platform that combines the power of LangFlow for visual workflow design with a modern React frontend and FastAPI backend. Build, test, and deploy intelligent agents through an intuitive cyberpunk-themed interface.

## 🚀 Quick Start

```bash
# Start all services
./start-dev.sh

# Access the applications:
# - Frontend: http://localhost:8080
# - Backend API: http://localhost:8000
# - LangFlow UI: http://localhost:7860

# Stop all services
./stop-dev.sh
```

## 📚 Documentation

- [Monorepo Overview](README_MONOREPO.md) - Detailed project structure and architecture
- [Run Commands](RUN_COMMANDS.md) - Step-by-step development guide
- [LangFlow Setup](langflow/README.md) - LangFlow service configuration
- [Backend API](langflow-backend/README.md) - FastAPI backend documentation
- [Web Client](web-client/README.md) - Frontend development guide

## 🏗️ Architecture

Ragamuffin is a monorepo containing three main services:

1. **LangFlow** (`:7860`) - Visual workflow designer for AI agents
2. **FastAPI Backend** (`:8000`) - Flow management and execution API
3. **React Frontend** (`:8080`) - Modern UI for agent interaction

## ⚠️ Security Note

This scaffold is for **development purposes only**. Before production deployment:

- Add authentication and authorization
- Validate and sandbox flow execution
- Restrict tool access in flows
- Configure secure CORS policies
- Use secrets management for API keys

## 📝 License

See repository license for details.