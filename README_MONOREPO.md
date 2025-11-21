# Ragamuffin Monorepo

![Ragamuffin AI Platform](https://via.placeholder.com/1200x600/1a1a2e/16f4d0?text=Ragamuffin+Visual+AI+Agent+Platform)

## Overview

**Ragamuffin** is a comprehensive monorepo for building, managing, and executing AI agents visually. The name "Ragamuffin" reflects the scrappy, resourceful nature of the platform - piecing together powerful AI capabilities from various sources into a cohesive, user-friendly experience.

The platform consists of three integrated services that work together to provide a complete agent-building experience:

### 🎨 LangFlow (Port 7860)
Visual workflow designer for creating AI agent flows. Build complex agent logic using a drag-and-drop interface without writing code.

### 🚀 FastAPI Backend (Port 8000)
Robust API layer that manages flow persistence, validation, and execution. Gracefully handles missing dependencies and provides clear error messages.

**Key Endpoints:**
- `POST /save_flow/` - Save flow JSON files
- `GET /list_flows/` - List all saved flows
- `GET /get_flow/{name}` - Retrieve specific flow
- `POST /run_flow/` - Execute a flow with user input

### 🎭 React Frontend (Port 8080)
Modern, cyberpunk-themed UI built with Vite, React, and TypeScript. Features the Orbitron font and a sleek interface for interacting with your agents.

**Main Features:**
- **Dashboard** - Overview and metrics
- **Playground** - Test and interact with agents
- **Datasets** - Manage training data
- **Agent Builder** - Create and edit flows visually

## 🏗️ Project Structure

```
ragamuffin/
├── docker-compose.yml          # Orchestrates all services
├── start-dev.sh               # Quick start script
├── stop-dev.sh                # Shutdown script
├── README.md                  # Top-level overview
├── README_MONOREPO.md         # This file
├── RUN_COMMANDS.md            # Detailed run guide
│
├── langflow/                  # LangFlow service
│   ├── Dockerfile
│   └── README.md
│
├── langflow-backend/          # FastAPI backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── flows/                 # Persistent flow storage
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py           # API implementation
│   └── README.md
│
└── web-client/                # React frontend
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

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Running the Stack

```bash
# Clone and enter the repository
git clone <repository-url>
cd rag7

# Start all services
./start-dev.sh

# Wait for services to initialize (30-60 seconds)
# Then access:
# - Frontend: http://localhost:8080
# - Backend API: http://localhost:8000
# - Backend Docs: http://localhost:8000/docs
# - LangFlow: http://localhost:7860
```

### Stopping the Stack

```bash
./stop-dev.sh
```

## 🔧 Development

### Backend Development
```bash
cd langflow-backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd web-client
npm install
npm run dev
```

## 🔒 Security Considerations

**⚠️ IMPORTANT: This scaffold is for development only!**

Before production deployment, you MUST:

1. **Authentication & Authorization**
   - Add user authentication (JWT, OAuth2, etc.)
   - Implement role-based access control
   - Secure all API endpoints

2. **Flow Validation & Sandboxing**
   - Validate flow JSON structure before execution
   - Sandbox flow execution to prevent code injection
   - Restrict available tools and modules
   - Set resource limits (CPU, memory, time)

3. **CORS Configuration**
   - Replace permissive CORS with specific origins
   - Use environment variables for allowed origins
   - Implement CSRF protection

4. **Secrets Management**
   - Never commit API keys or credentials
   - Use environment variables or secrets managers
   - Rotate keys regularly

5. **Input Validation**
   - Validate all user inputs
   - Sanitize file uploads
   - Implement rate limiting

6. **Monitoring & Logging**
   - Add comprehensive logging
   - Monitor for suspicious activity
   - Implement alerting

## 📦 Flow Persistence

Flows are persisted to `./langflow-backend/flows/` and mounted as a Docker volume. This ensures your agent workflows survive container restarts.

## 🎨 UI Theme

The frontend uses a cyberpunk aesthetic with:
- **Font**: Orbitron (Google Fonts)
- **Color Scheme**: Dark backgrounds (#1a1a2e) with neon accents (#16f4d0, #e94560)
- **Style**: Futuristic, tech-forward design

## 🛠️ Customization

### Adding Custom Components
Place new React components in `web-client/src/components/` and import them where needed.

### Extending the API
Add new endpoints in `langflow-backend/app/main.py` following the existing pattern.

### Custom Flows
Create flows in LangFlow UI (port 7860) and they'll automatically sync to the backend's `/flows/` directory.

## 🐛 Troubleshooting

### LangFlow Not Available
The backend gracefully handles missing LangFlow by returning simulated responses. Check logs for warnings.

### Port Conflicts
If ports 7860, 8000, or 8080 are in use, modify `docker-compose.yml` to use different ports.

### Build Failures
Ensure Docker has sufficient resources. Try `docker-compose down -v` then rebuild.

## 🤝 Contributing

This is a scaffold project. Customize it for your needs:
1. Add authentication
2. Implement real agent logic
3. Extend the UI with your features
4. Add tests and CI/CD
5. Deploy securely

## 📄 Next Steps

1. **Secure the Stack** - Follow security guidelines above
2. **Add Authentication** - Implement user management
3. **Build Agents** - Create your first flow in LangFlow
4. **Extend UI** - Customize the frontend for your use case
5. **Deploy** - Set up production infrastructure with proper security

---

Built with ❤️ for the AI agent building community.
