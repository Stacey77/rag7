# Epic Platform Monorepo - Complete Overview

## 🎯 Vision

The **Epic Platform (Ragamuffin)** is a full-stack monorepo enabling visual LangFlow agent building and execution through an integrated FastAPI backend and modern Vite+React+TypeScript frontend.

## 🎨 UI Inspiration
![Cyberpunk UI Reference](https://github.com/user-attachments/assets/placeholder-ui-reference.png)

*Our interface is inspired by cyberpunk aesthetics with the Orbitron font and neon accents.*

## 📦 Monorepo Structure

```
rag7/
├── docker-compose.yml          # Orchestrates all services
├── start-dev.sh                # Quick start script
├── stop-dev.sh                 # Quick stop script
├── langflow/                   # LangFlow visual builder service
│   ├── Dockerfile
│   └── README.md
├── langflow-backend/           # FastAPI backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── flows/                  # Persisted flow definitions
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py            # API endpoints
│   └── README.md
└── web-client/                 # React frontend
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   └── ...
    └── README.md
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### First-Time Setup

```bash
# Clone the repository
git clone https://github.com/Stacey77/rag7.git
cd rag7

# Start all services
./start-dev.sh
```

### Access Services

- **LangFlow UI**: http://localhost:7860
- **Backend API**: http://localhost:8000
- **Frontend App**: http://localhost:8080
- **API Docs**: http://localhost:8000/docs

## 🔧 Development Workflow

1. **Design Flows** in LangFlow (`:7860`)
2. **Export Flows** as JSON from LangFlow
3. **Upload Flows** via AgentBuilder page (`:8080`)
4. **Execute Flows** through the web interface

## 🏗️ Service Details

### LangFlow Service
- Visual flow builder for AI agents
- Runs on port 7860
- No authentication by default (add in production!)

### Backend Service
- FastAPI with auto-generated OpenAPI docs
- Manages flow storage and execution
- CORS enabled for localhost development
- Graceful fallback when langflow is unavailable

### Frontend Service
- Built with Vite+React+TypeScript
- Cyberpunk-themed UI with Orbitron font
- Components: Sidebar, AIBrain, Conversation (STT/TTS)
- Pages: Dashboard, Playground, Datasets, AgentBuilder

## 🛡️ Security Considerations

⚠️ **IMPORTANT**: This scaffold is for development only.

**Before production deployment:**
- ✅ Add authentication & authorization
- ✅ Validate uploaded flows before execution
- ✅ Sandbox flow execution environment
- ✅ Configure proper CORS policies
- ✅ Use secrets management (not .env files)
- ✅ Enable HTTPS/TLS
- ✅ Implement rate limiting
- ✅ Add input validation and sanitization
- ✅ Regular security audits

**Current security gaps:**
- No authentication on any service
- CORS allows all origins from localhost
- Flows execute without validation
- No sandboxing of flow execution
- Simulated responses when langflow unavailable (for development)

## 🗄️ Data Persistence

- **Flow Storage**: `./langflow-backend/flows/` (mounted volume)
- Flows persist across container restarts
- JSON format for easy version control

## 📚 Additional Documentation

- [Run Commands Guide](./RUN_COMMANDS.md)
- [LangFlow Configuration](./langflow/README.md)
- [Backend API Details](./langflow-backend/README.md)

## 🤝 Contributing

See individual service READMEs for development guidelines.

## 📝 Next Steps

1. Explore LangFlow at http://localhost:7860
2. Create a simple flow and export as JSON
3. Upload the flow via AgentBuilder page
4. Test execution through the API or web interface
5. Customize the cyberpunk theme in `web-client/src/styles.css`

---

**Note**: Backend gracefully falls back to simulated responses if langflow Python library is unavailable, allowing frontend development to proceed independently.
