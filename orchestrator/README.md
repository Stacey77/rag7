# FortFail Orchestrator

Central orchestration service for the FortFail backup and restore system.

## Features

- **JWT Authentication**: Secure token-based authentication using registration secrets
- **Snapshot Management**: Store and retrieve backup snapshots with S3/MinIO
- **Restore Jobs**: Create and track restore operations across agents
- **Real-time Events**: WebSocket streaming of system events
- **Write-Ahead Log (WAL)**: Persistent audit trail of all operations
- **Agent Management**: Track and communicate with registered agents

## API Endpoints

### Authentication
- `POST /auth/token` - Mint JWT token using registration secret

### Snapshots
- `POST /snapshots` - Create snapshot metadata, get presigned upload URL
- `POST /snapshots/{id}/object` - Upload snapshot via multipart (with checksum validation)
- `GET /snapshots/{id}/object` - Download snapshot object

### Restore Jobs
- `POST /restore-jobs` - Create new restore job
- `GET /restore-jobs/{id}` - Get job status

### Agents
- `GET /agents` - List all registered agents
- `GET /agent/{id}/commands` - Get pending commands for agent
- `POST /agent/{id}/events` - Post event from agent

### Health
- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe (checks DB)

### WebSocket
- `WS /ws?token=<jwt>` - Real-time event stream

### UI
- `GET /control` - Static control panel UI
- `GET /docs` - OpenAPI documentation

## Configuration

All configuration via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ORCH_JWT_SECRET` | Secret for JWT signing | `dev-jwt-secret-change-in-production` |
| `ORCH_REG_SECRET` | Registration secret for minting tokens | `dev-reg-secret-change-in-production` |
| `DATABASE_URL` | Database connection string | `sqlite:///./orchestrator.db` |
| `S3_ENDPOINT` | S3/MinIO endpoint | `http://minio:9000` |
| `S3_ACCESS_KEY` | S3 access key | `minioadmin` |
| `S3_SECRET_KEY` | S3 secret key | `minioadmin` |
| `S3_BUCKET` | S3 bucket name | `fortfail-snapshots` |
| `WAL_PATH` | Write-ahead log file path | `/data/orchestrator_wal.log` |

## Running Locally

### With Docker
```bash
docker build -t fortfail-orchestrator .
docker run -p 8000:8000 \
  -e ORCH_JWT_SECRET=your-secret \
  -e ORCH_REG_SECRET=your-reg-secret \
  fortfail-orchestrator
```

### With Python
```bash
pip install -r requirements.txt
python main.py
```

### With Docker Compose
See root `docker-compose.yml` for full stack deployment.

## Development

The orchestrator uses:
- **FastAPI** for REST API
- **SQLAlchemy** for database ORM
- **boto3** for S3/MinIO interaction
- **PyJWT** for authentication
- **WebSockets** for real-time events

## Security Notes

⚠️ **This is a PoC implementation**

- All secrets must be provided via environment variables
- Never commit real secrets to version control
- Use strong, random secrets in production
- Consider using a secrets manager (Vault, AWS Secrets Manager, etc.)
- Enable HTTPS/TLS in production
- Restrict CORS origins in production
- Implement rate limiting and input validation

## Database Schema

### Snapshots
- `id` (string, primary key)
- `agent_id` (string, indexed)
- `checksum` (string)
- `size` (integer)
- `created_at` (datetime)
- `metadata` (JSON text)

### RestoreJobs
- `id` (string, primary key)
- `snapshot_id` (string)
- `target_agent_id` (string, indexed)
- `status` (string: pending/in_progress/completed/failed)
- `created_at` (datetime)
- `updated_at` (datetime)
- `logs` (JSON array)

### Commands
- `id` (string, primary key)
- `agent_id` (string, indexed)
- `job_id` (string)
- `command_type` (string)
- `payload` (JSON text)
- `status` (string: pending/sent/completed/failed)
- `created_at` (datetime)
- `updated_at` (datetime)

## License

MIT License - see LICENSE file
