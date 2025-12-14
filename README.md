# Agentic Agent Platform

Production-ready scaffold for an autonomous agentic AI platform with human oversight, RBAC, and ML pipeline integration.

## Features

### Core Capabilities
- **FastAPI Backend**: Async Python backend with SQLAlchemy and PostgreSQL
- **React Frontend**: Vite-powered oversight dashboard with real-time updates
- **Reliable Orchestration**: Task ack/retry flow with exponential backoff and escalation
- **Persistent Event Store**: Complete audit trail in PostgreSQL with Alembic migrations
- **Authentication & RBAC**: OIDC-based auth with role-based access control
- **ML Pipeline Integration**: Training job runner and model registry
- **Real-time Updates**: WebSocket-based event streaming for oversight

### Task State Machine
```
queued → assigned → acked → in_progress → completed → verified
                     ↓
                  failed → escalated
```

### RBAC Roles
- **admin**: Full system access
- **reviewer**: Override decisions, escalate tasks
- **agent_manager**: Manage agents, escalate tasks
- **viewer**: Read-only access

## Quick Start

### Prerequisites
- Docker and Docker Compose
- (Optional) Python 3.11+ and Node.js 20+ for local development

### Running with Docker Compose

1. Clone the repository:
```bash
git clone https://github.com/Stacey77/rag7.git
cd rag7
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start all services:
```bash
docker-compose up --build
```

This will start:
- **PostgreSQL** on port 5432
- **Redis** on port 6379
- **Backend API** on port 8000
- **Frontend UI** on port 80

4. Access the application:
- Frontend: http://localhost
- API docs: http://localhost:8000/docs
- API: http://localhost:8000

5. Login credentials (dev mode):
- Username: any username
- Password: any password
- (Dev mode grants all roles)

### Local Development

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/agentic"

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### Running Tests

#### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

#### Frontend Tests
```bash
cd frontend
npm run lint
npm run build
```

## Architecture

### Backend Structure
```
backend/
├── app/
│   ├── agents/           # Agent implementations
│   │   ├── communication.py  # Redis pub/sub, ack protocol
│   │   ├── decision.py       # Decision-making logic
│   │   ├── delegation.py     # Task assignment, retry, escalation
│   │   └── learning.py       # ML pipeline integration
│   ├── api/              # REST API endpoints
│   │   ├── auth.py          # Authentication & RBAC
│   │   ├── decisions.py     # Task management
│   │   ├── oversight_ws.py  # WebSocket events
│   │   └── admin.py         # Admin operations
│   ├── db/               # Database layer
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── crud.py          # Database operations
│   │   ├── session.py       # DB session management
│   │   └── base.py          # Exports
│   ├── core.py           # Configuration & utilities
│   └── main.py           # FastAPI application
├── alembic/              # Database migrations
│   ├── versions/
│   │   └── 001_initial.py
│   └── env.py
├── tests/                # Test suite
├── Dockerfile
└── requirements.txt
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── Login.jsx            # Authentication UI
│   │   └── OversightDashboard.jsx  # Main dashboard
│   ├── lib/
│   │   ├── auth.js              # Auth client
│   │   └── websocket.js         # WebSocket client
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── public/
├── Dockerfile
├── nginx.conf
├── vite.config.js
└── package.json
```

## Configuration

### Environment Variables

See `.env.example` for all configuration options.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_HOST`, `REDIS_PORT`: Redis configuration
- `SECRET_KEY`: JWT signing key (change in production!)
- `OIDC_ISSUER`, `OIDC_CLIENT_ID`, `OIDC_CLIENT_SECRET`: OIDC provider config (optional)

### OIDC Configuration

For production, configure an OIDC provider:

1. Set OIDC environment variables in `.env`
2. Configure your OIDC provider with:
   - Redirect URI: `http://your-domain/auth/callback`
   - Allowed origins: `http://your-domain`

3. Update backend to use proper JWT verification with JWKS

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints

#### Authentication
- `POST /auth/login` - Login (dev mode)
- `GET /auth/me` - Get current user
- `GET /auth/roles` - List available roles

#### Tasks & Decisions
- `POST /decisions/task` - Create new task
- `GET /decisions/task/{id}` - Get task details
- `POST /decisions/override` - Override decision (admin/reviewer)
- `POST /decisions/escalate` - Escalate task (admin/reviewer/agent_manager)

#### Admin
- `POST /admin/agents` - Create agent (admin/agent_manager)
- `GET /admin/agents` - List agents
- `GET /admin/models` - List models
- `POST /admin/training/trigger` - Trigger training job
- `GET /admin/stats` - Get system statistics

#### WebSocket
- `WS /ws/oversight?token=<jwt>` - Real-time event stream

## Development Workflow

### Adding New Agent Types

1. Add enum value to `AgentType` in `backend/app/db/models.py`
2. Implement agent logic in `backend/app/agents/`
3. Register agent in delegation system
4. Create migration if needed

### Adding New API Endpoints

1. Create endpoint in appropriate router in `backend/app/api/`
2. Add RBAC checks using `require_role()` or `require_any_role()`
3. Log actions with `AuditCRUD.create_audit()`
4. Add tests in `backend/tests/`

### Database Migrations

```bash
# Create new migration
cd backend
alembic revision -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Production Considerations

### Security
- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Configure proper OIDC provider
- [ ] Enable HTTPS/TLS
- [ ] Implement rate limiting
- [ ] Add request validation and sanitization
- [ ] Configure CORS properly
- [ ] Rotate credentials regularly

### Scalability
- [ ] Use connection pooling for database
- [ ] Implement Redis Sentinel for HA
- [ ] Add caching layer (Redis)
- [ ] Use message queue for background tasks (Celery)
- [ ] Implement horizontal scaling with load balancer

### Monitoring & Observability
- [ ] Add structured logging
- [ ] Integrate APM (e.g., DataDog, New Relic)
- [ ] Set up metrics (Prometheus)
- [ ] Configure alerts
- [ ] Add health check endpoints

### Deployment
- [ ] Create Kubernetes manifests
- [ ] Set up CI/CD pipeline
- [ ] Implement blue-green deployment
- [ ] Configure backups for PostgreSQL
- [ ] Set up log aggregation

## Testing

### Unit Tests
```bash
cd backend
pytest tests/ -v
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Load Testing
Use tools like `locust` or `k6` to test scalability.

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running: `docker-compose ps postgres`
- Check connection string in `.env`
- Verify migrations: `alembic current`

### Redis Connection Issues
- Ensure Redis is running: `docker-compose ps redis`
- Check Redis logs: `docker-compose logs redis`

### Frontend Can't Connect to Backend
- Verify backend is running: `curl http://localhost:8000/health`
- Check CORS configuration in backend
- Review browser console for errors

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and add tests
4. Run tests: `pytest` and `npm test`
5. Commit: `git commit -am 'Add new feature'`
6. Push: `git push origin feature/my-feature`
7. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Roadmap

- [ ] Implement actual ML training pipeline with scikit-learn/TensorFlow
- [ ] Add more sophisticated decision algorithms
- [ ] Implement agent performance metrics and monitoring
- [ ] Add multi-tenancy support
- [ ] Create Kubernetes deployment manifests
- [ ] Add integration with external AI services (OpenAI, Anthropic)
- [ ] Implement A/B testing for agent decisions
- [ ] Add data export and reporting features