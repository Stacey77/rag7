# Epic Platform Monorepo

Welcome to the Epic Platform! This monorepo contains a complete full-stack starter for building AI-powered applications with LangFlow, FastAPI, and React.

## 🎨 Visual Reference

The platform UI is inspired by a cyberpunk aesthetic with the Orbitron font and a futuristic design. See the reference image for the visual inspiration behind the platform's look and feel.

## 🏗️ Architecture

This monorepo consists of three main components:

### 1. **LangFlow Container** (`/langflow`)
- Visual flow builder for AI workflows
- Runs on port **7860**
- Provides a drag-and-drop interface for creating AI pipelines

### 2. **FastAPI Backend** (`/langflow-backend`)
- RESTful API for managing LangFlow flows
- Runs on port **8000**
- Endpoints:
  - `POST /save_flow/` - Save a LangFlow JSON
  - `GET /list_flows/` - List all saved flows
  - `GET /get_flow/{flow_name}` - Retrieve a specific flow
  - `POST /run_flow/` - Execute a flow with user input

### 3. **React Frontend** (`/web-client`)
- Modern web client built with Vite + React + TypeScript
- Runs on port **3000**
- Features:
  - Dashboard with cyberpunk theme
  - Agent Builder for creating and managing flows
  - Playground for testing
  - Datasets management
  - AI Brain visualization
  - Voice input/output (STT/TTS)

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose installed
- At least 4GB of available RAM
- Ports 3000, 7860, and 8000 available

### Start the Platform

```bash
# Option 1: Use the helper script
./start-dev.sh

# Option 2: Use Docker Compose directly
docker-compose up --build
```

### Access the Services

Once all services are running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000 (docs at http://localhost:8000/docs)
- **LangFlow UI**: http://localhost:7860

### Stop the Platform

```bash
# Option 1: Use the helper script
./stop-dev.sh

# Option 2: Use Docker Compose directly
docker-compose down
```

## 📁 Project Structure

```
rag7/
├── docker-compose.yml          # Orchestrates all services
├── README_MONOREPO.md          # This file
├── RUN_COMMANDS.md             # Detailed run commands
├── start-dev.sh                # Quick start script
├── stop-dev.sh                 # Quick stop script
│
├── langflow/                   # LangFlow container
│   ├── Dockerfile
│   └── README.md
│
├── langflow-backend/           # FastAPI backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── README.md
│   └── app/
│       ├── __init__.py
│       └── main.py             # FastAPI application
│
└── web-client/                 # React frontend
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    ├── index.html
    ├── .env
    ├── README.md
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── styles.css
        ├── components/         # Reusable components
        │   ├── Sidebar.tsx
        │   ├── AIBrain.tsx
        │   ├── SectionAgent.tsx
        │   └── Conversation.tsx
        └── pages/              # Application pages
            ├── Dashboard.tsx
            ├── Playground.tsx
            ├── Datasets.tsx
            └── AgentBuilder.tsx
```

## 🔧 Development

### Running Individual Services

Each service can be run independently for development:

```bash
# LangFlow only
cd langflow && docker build -t epic-langflow . && docker run -p 7860:7860 epic-langflow

# Backend only
cd langflow-backend && docker build -t epic-backend . && docker run -p 8000:8000 epic-backend

# Frontend only (requires Node.js)
cd web-client && npm install && npm run dev
```

### Hot Reloading

The docker-compose setup includes volume mounts for hot reloading:
- Backend: Changes to `/langflow-backend/app` are reflected immediately
- Frontend: Rebuild the container or run locally with `npm run dev`

## 🔐 Security Notes

⚠️ **Important**: This is a development setup. Before deploying to production:

1. **Enable Authentication**: Add user authentication to the backend
2. **Secure CORS**: Restrict CORS origins to your production domain
3. **Validate Flows**: Add flow validation and sanitization
4. **Use HTTPS**: Configure SSL/TLS certificates
5. **Environment Variables**: Use secrets management for sensitive data
6. **Persistent Storage**: Configure proper database and file storage

## 🎯 Next Steps

1. **Explore LangFlow**: Open http://localhost:7860 and create your first flow
2. **Test the Backend**: Visit http://localhost:8000/docs for API documentation
3. **Build Agents**: Use the Agent Builder page to create and manage flows
4. **Customize the UI**: Modify the cyberpunk theme in `web-client/src/styles.css`
5. **Add Integrations**: Connect to external APIs and services

## 📚 Additional Resources

- [LangFlow Documentation](https://docs.langflow.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

This project is part of the Epic Platform initiative.
