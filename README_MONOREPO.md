# Ragamuffin Monorepo Structure

This document describes the architecture and organization of the Ragamuffin monorepo.

## 📁 Repository Structure

```
rag7/
├── docker-compose.yml          # Orchestrates all services
├── start-dev.sh                # Start development environment
├── stop-dev.sh                 # Stop development environment
├── README.md                   # Main project README
├── README_MONOREPO.md          # This file
├── RUN_COMMANDS.md             # Command reference
│
├── langflow/                   # LangFlow container service
│   ├── Dockerfile
│   └── README.md
│
├── langflow-backend/           # FastAPI backend service
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── README.md
│   ├── flows/                  # Persisted flow definitions
│   └── app/
│       ├── __init__.py
│       └── main.py             # FastAPI application
│
└── web-client/                 # React + TypeScript frontend
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    ├── index.html
    ├── .env
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── styles.css
        ├── components/
        │   ├── Sidebar.tsx
        │   ├── AIBrain.tsx
        │   ├── SectionAgent.tsx
        │   └── Conversation.tsx
        └── pages/
            ├── Dashboard.tsx
            ├── Playground.tsx
            ├── Datasets.tsx
            └── AgentBuilder.tsx
```

## 🏗️ Architecture

### LangFlow Service (Port 7860)
- Provides visual interface for building AI agent flows
- Data persisted in Docker volume `langflow_data`
- Accessible at http://localhost:7860

### Backend Service (Port 8000)
- FastAPI REST API for flow management
- Endpoints:
  - `POST /save_flow/` - Save a flow definition
  - `GET /list_flows/` - List all saved flows
  - `GET /get_flow/{flow_name}` - Retrieve a specific flow
  - `POST /run_flow/` - Execute a flow with user input
- Flows stored in `./langflow-backend/flows` directory
- Accessible at http://localhost:8000

### Frontend Service (Port 8080)
- React + TypeScript + Vite web application
- Pages:
  - Dashboard - Overview and metrics
  - Playground - Interactive agent testing
  - Datasets - Data management
  - AgentBuilder - Flow creation and management
- Cyberpunk-themed UI with Orbitron font
- Accessible at http://localhost:8080

## 🔗 Service Communication

```
User Browser (8080)
    ↓
React Frontend
    ↓
FastAPI Backend (8000)
    ↓
LangFlow Service (7860)
```

## 🐳 Docker Networking

All services communicate via the `ragamuffin-network` bridge network.

## 💾 Data Persistence

- **LangFlow data**: Docker volume `langflow_data`
- **Flow definitions**: Host-mounted directory `./langflow-backend/flows`

## 🔒 Security Considerations

**⚠️ This is a development setup. For production deployment:**

1. **CORS Configuration**: Restrict allowed origins in backend
2. **Flow Validation**: Add comprehensive input validation
3. **Authentication**: Implement user authentication and authorization
4. **Secrets Management**: Use environment variables or secrets manager
5. **Network Security**: Add reverse proxy (nginx/traefik) with TLS
6. **Volume Permissions**: Review file permissions for mounted volumes

## 🚦 Next Steps

1. Implement authentication system
2. Add flow validation and sanitization
3. Set up persistent database (PostgreSQL)
4. Add monitoring and logging (Prometheus, Grafana)
5. Create CI/CD pipeline
6. Write comprehensive tests
7. Add API documentation (OpenAPI/Swagger)
