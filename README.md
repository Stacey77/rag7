# Agentic Agent Platform

A production-ready scaffold for building autonomous agent systems with human oversight capabilities.

## Features

- **Modular FastAPI Backend** - Async Python backend with SQLAlchemy 2.0
- **React Oversight UI** - Real-time dashboard for monitoring and controlling agents
- **Reliable Orchestration** - Ack/retry flow with exponential backoff and escalation
- **Persistent Event Store** - PostgreSQL with Alembic migrations
- **OIDC Authentication & RBAC** - Secure authentication with role-based access control
- **ML Pipeline Integration** - Training job runner and model registry

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                         │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │ Login/Auth Flow │  │ Oversight        │  │ RBAC-aware    │  │
│  │ (OIDC support)  │  │ Dashboard        │  │ UI Controls   │  │
│  └─────────────────┘  └──────────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │ REST API + WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                        Backend (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐│
│  │ Auth API     │  │ Decisions API│  │ Admin API              ││
│  │ (JWT/OIDC)   │  │ (Tasks,Events│  │ (Agents, Models, Jobs) ││
│  └──────────────┘  └──────────────┘  └────────────────────────┘│
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     Agent Systems                         │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────┐ │  │
│  │  │Communication│ │ Decision  │ │ Delegation │ │Learning│ │  │
│  │  │ (Ack/Retry) │ │ System    │ │ System     │ │ System │ │  │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
    ┌────┴────┐          ┌────┴────┐          ┌────┴────┐
    │PostgreSQL│          │  Redis  │          │ Celery  │
    │(Events,  │          │(Pub/Sub │          │(Training│
    │ Tasks)   │          │ Acks)   │          │ Jobs)   │
    └─────────┘          └─────────┘          └─────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for local development)

### Running with Docker Compose

```bash
# Clone the repository
git clone https://github.com/Stacey77/rag7.git
cd rag7

# Start all services
docker-compose up --build

# Access the UI at http://localhost:3000
# API available at http://localhost:8000
```

### Local Development

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/agentic
export REDIS_URL=redis://localhost:6379/0

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Environment Variables

### Backend

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql+asyncpg://postgres:postgres@localhost:5432/agentic` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `JWT_SECRET_KEY` | Secret key for JWT signing | `dev-secret-key-change-in-production` |
| `OIDC_ISSUER` | OIDC provider issuer URL | - |
| `OIDC_CLIENT_ID` | OIDC client ID | - |
| `OIDC_CLIENT_SECRET` | OIDC client secret | - |
| `TASK_ACK_TIMEOUT_SECONDS` | Task acknowledgement timeout | `30` |
| `TASK_MAX_RETRIES` | Maximum retry attempts | `3` |

## API Endpoints

### Authentication

- `POST /api/v1/auth/token` - Login with username/password
- `GET /api/v1/auth/me` - Get current user profile
- `GET /api/v1/auth/oidc/config` - Get OIDC configuration
- `POST /api/v1/auth/oidc/callback` - OIDC callback handler

### Decisions

- `POST /api/v1/decisions/task` - Create a new task
- `GET /api/v1/decisions/task/{id}` - Get task by ID
- `GET /api/v1/decisions/tasks` - List tasks
- `PATCH /api/v1/decisions/task/{id}/state` - Update task state
- `POST /api/v1/decisions/task/{id}/override` - Override decision (reviewer+)
- `POST /api/v1/decisions/task/{id}/escalate` - Escalate task
- `GET /api/v1/decisions/events` - Get events
- `GET /api/v1/decisions/escalations` - Get escalated tasks

### Admin

- `POST /api/v1/admin/agents` - Create agent
- `GET /api/v1/admin/agents` - List agents
- `POST /api/v1/admin/models` - Register model
- `GET /api/v1/admin/models` - List models
- `POST /api/v1/admin/training-jobs` - Create training job
- `GET /api/v1/admin/audits` - Get audit log

### WebSocket

- `WS /api/v1/oversight/ws?token={jwt}` - Real-time oversight stream

## RBAC Roles

| Role | Permissions |
|------|-------------|
| `admin` | Full access to all endpoints |
| `reviewer` | Override decisions, view escalations |
| `agent_manager` | Manage agents, create tasks, view stats |
| `viewer` | Read-only access to tasks and events |

## Task State Machine

```
queued → assigned → acked → in_progress → completed → verified
                  ↓              ↓
               (timeout)     (failure)
                  ↓              ↓
              retry (N times) → escalated
```

## Database Schema

The platform uses the following tables:

- `events` - Event store for all system events
- `tasks` - Task definitions and state
- `agents` - Agent configurations
- `audits` - Audit log for administrative actions
- `feedback` - Feedback for agent learning
- `models` - Model registry
- `training_jobs` - Training job tracking

## Testing

```bash
cd backend

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Next Steps

- [ ] Harden authentication (refresh tokens, session management)
- [ ] Add OpenTelemetry for observability
- [ ] Kubernetes manifests for production deployment
- [ ] Implement actual ML training pipeline with Celery
- [ ] Add rate limiting and API throttling
- [ ] Implement agent health monitoring

## License

MIT