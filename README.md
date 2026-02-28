# Epic Platform - RAG7 Monorepo

Welcome to the Epic Platform! This repository contains a complete monorepo setup for building AI-powered applications with LangFlow, FastAPI, and React.

## 🚀 Quick Start

```bash
# Start all services
./start-dev.sh

# Stop all services
./stop-dev.sh
```

**Access the platform:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000 (docs at /docs)
- LangFlow UI: http://localhost:7860

## 📚 Documentation

- **[README_MONOREPO.md](./README_MONOREPO.md)** - Complete architecture overview and quick start guide
- **[RUN_COMMANDS.md](./RUN_COMMANDS.md)** - Step-by-step commands for running and managing services

## 🏗️ Project Structure

- `/langflow` - LangFlow visual builder container
- `/langflow-backend` - FastAPI backend for flow management
- `/web-client` - React + TypeScript frontend

## 🔧 Prerequisites

- Docker & Docker Compose
- 4GB+ available RAM
- Ports 3000, 7860, 8000 available

## 🎯 Features

- **Visual Flow Builder**: Drag-and-drop AI workflow creation with LangFlow
- **RESTful API**: FastAPI backend for saving, listing, and running flows
- **Modern UI**: Cyberpunk-themed React frontend with Orbitron font
- **Agent Builder**: Create and manage AI agents
- **Voice Interface**: Speech-to-text and text-to-speech capabilities
- **Docker Compose**: One-command setup for the entire stack

## 🔐 Security Note

This is a development setup. Before production deployment:
- Enable authentication
- Secure CORS settings
- Validate and sanitize flows
- Use HTTPS
- Implement secrets management

See README_MONOREPO.md for detailed security recommendations.

## 📄 License

Part of the Epic Platform initiative.