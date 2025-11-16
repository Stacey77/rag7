# rag7 - Epic Platform

<img src="https://via.placeholder.com/1200x400/1a1a2e/16e0bd?text=Epic+Platform+%7C+AI-Powered+RAG+System" alt="Epic Platform UI" />

## Overview

Epic Platform is a comprehensive AI-powered monorepo featuring LangFlow visual flow building, a FastAPI backend for flow management, and a cyberpunk-themed React frontend with real-time conversation capabilities.

## Quick Start

```bash
# Start all services
./start-dev.sh

# Stop all services
./stop-dev.sh
```

## Architecture

- **LangFlow** (Port 7860): Visual AI workflow builder
- **Backend API** (Port 8000): FastAPI service for flow management
- **Web Client** (Port 8080): React/TypeScript UI with STT/TTS

## Documentation

- [Monorepo Guide](./README_MONOREPO.md) - Architecture and service details
- [Run Commands](./RUN_COMMANDS.md) - Complete command reference
- [LangFlow Setup](./langflow/README.md) - LangFlow configuration
- [Backend API](./langflow-backend/README.md) - API development guide
- [Frontend Development](./web-client/README.md) - UI development guide

## Features

- 🎨 Visual flow building with LangFlow
- 🚀 RESTful API for flow management
- 💬 Real-time conversation with STT/TTS
- 🎯 Agent builder interface
- 📊 Dashboard with metrics
- 🔧 Playground for testing flows
- 📁 Dataset management
- 🎭 Cyberpunk-themed UI with Orbitron font

## Requirements

- Docker 20.10+
- Docker Compose v2.0+
- 4GB+ RAM
- Ports 7860, 8000, 8080 available

## Services

Visit the running services:
- LangFlow UI: http://localhost:7860
- Backend API Docs: http://localhost:8000/docs
- Frontend UI: http://localhost:8080

## Next Steps

For production deployment, consider:
- Configure secure CORS origins
- Add flow schema validation
- Implement authentication/authorization
- Set up persistent database storage
- Add monitoring and logging