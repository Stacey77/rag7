# Ragamuffin Monorepo Documentation

![Platform Overview](<img>)

## Overview
Ragamuffin is a comprehensive AI orchestration platform built as a monorepo. It provides a complete solution for designing, managing, and executing AI agent workflows through visual flow design, a robust backend API, and an intuitive web interface.

## Monorepo Structure

```
rag7/
├── docker-compose.yml          # Orchestrates all services
├── README.md                    # Top-level project summary
├── README_MONOREPO.md          # This file - detailed monorepo docs
├── RUN_COMMANDS.md             # Step-by-step commands
├── start-dev.sh                # Quick start script
├── stop-dev.sh                 # Quick stop script
│
├── langflow/                   # LangFlow service
│   ├── Dockerfile              # LangFlow container definition
│   └── README.md               # LangFlow documentation
│
├── langflow-backend/           # FastAPI backend service
│   ├── Dockerfile              # Backend container definition
│   ├── requirements.txt        # Python dependencies
│   ├── flows/                  # Persisted flow files
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py             # FastAPI application
│   └── README.md               # Backend documentation
│
└── web-client/                 # React + TypeScript frontend
    ├── Dockerfile              # Multi-stage build with nginx
    ├── nginx.conf              # Nginx configuration (optional)
    ├── package.json            # Node dependencies
    ├── tsconfig.json           # TypeScript configuration
    ├── vite.config.ts          # Vite build configuration
    ├── index.html              # Entry HTML
    ├── .env                    # Environment variables
    ├── src/
    │   ├── main.tsx            # Application entry point
    │   ├── App.tsx             # Root component
    │   ├── styles.css          # Global styles (Orbitron font, cyberpunk theme)
    │   ├── components/
    │   │   ├── Sidebar.tsx
    │   │   ├── AIBrain.tsx
    │   │   ├── SectionAgent.tsx
    │   │   └── Conversation.tsx  # STT/TTS support
    │   └── pages/
    │       ├── Dashboard.tsx
    │       ├── Playground.tsx
    │       ├── Datasets.tsx
    │       └── AgentBuilder.tsx  # Flow management integration
    └── README.md               # Frontend documentation
```

## Service Architecture

### LangFlow Container (Port 7860)
- Visual AI flow designer
- Drag-and-drop interface for building AI workflows
- Runs on port 7860

### FastAPI Backend (Port 8000)
- RESTful API for flow management
- Endpoints:
  - `POST /save_flow/` - Upload and save flow JSON files
  - `GET /list_flows/` - List all saved flows
  - `GET /get_flow/{flow_name}` - Retrieve flow content
  - `POST /run_flow/` - Execute a flow with user input
- CORS enabled for localhost development
- Graceful fallback when LangFlow runtime unavailable

### Web Client (Port 8080)
- Modern React + TypeScript SPA
- Vite for fast development and optimized builds
- Cyberpunk-inspired UI with Orbitron font
- Real-time flow management through AgentBuilder page
- Multi-page architecture with routing

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Ports 7860, 8000, and 8080 available

### Running the Platform
```bash
# Make scripts executable (first time only)
chmod +x start-dev.sh stop-dev.sh

# Start all services
./start-dev.sh

# Access the platform
# Frontend: http://localhost:8080
# Backend API: http://localhost:8000/docs
# LangFlow: http://localhost:7860
```

### Stopping the Platform
```bash
./stop-dev.sh
```

## Development Workflow

1. **Design Flows**: Use LangFlow UI (port 7860) to visually design AI workflows
2. **Save Flows**: Export flows as JSON and upload via backend API or AgentBuilder UI
3. **Execute Flows**: Run flows through the backend API with custom inputs
4. **Monitor**: View flow execution results in the web interface

## Data Persistence
- Flow files are stored in `./langflow-backend/flows/`
- This directory is mounted into the backend container
- Files persist across container restarts

## Security Considerations
⚠️ **Important**: This scaffold is for development only. For production:
- Implement authentication and authorization
- Validate and sandbox flow execution
- Secure CORS configuration
- Add rate limiting and input validation
- Use HTTPS/TLS
- Implement proper secret management
- Review and audit all uploaded flows

## Next Steps
1. Test the basic setup
2. Customize the UI components
3. Add authentication layer
4. Implement flow validation
5. Set up production-grade storage
6. Configure monitoring and logging
