# Development Guide

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- Git
- Make (optional, for convenience commands)

### Initial Setup

1. **Clone the repository**:
```bash
git clone https://github.com/Stacey77/rag7.git
cd rag7
```

2. **Set up Python environment**:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
make install-dev
# or
pip install -r requirements.txt -r requirements-dev.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Development Workflow

### Running Locally

**Option 1: With Docker Compose (Recommended)**
```bash
# Start all services
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

**Option 2: Run Python app directly**
```bash
# Make sure dependencies are running
docker-compose up -d redis postgres qdrant

# Run the application
make run-local
# or
uvicorn src.main:app --reload --host 0.0.0.0 --port 8080
```

### Code Quality

**Formatting**:
```bash
# Format code with black and ruff
make format
```

**Linting**:
```bash
# Run ruff linter
make lint
```

**Type Checking**:
```bash
# Run mypy
make type-check
```

**Security Scanning**:
```bash
# Run bandit
make security-check
```

**All checks**:
```bash
# Run all quality checks
make all
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test types
make test-unit          # Unit tests only
make test-integration   # Integration tests
make test-orchestration # Agent orchestration tests
make test-chaos         # Chaos engineering tests
```

### Writing Tests

**Unit Test Example**:
```python
import pytest
from src.config import Settings

@pytest.mark.unit
def test_settings_defaults():
    """Test default settings values."""
    settings = Settings()
    assert settings.environment == "development"
    assert settings.log_level == "INFO"
```

**Integration Test Example**:
```python
import pytest
from src.llm import client

@pytest.mark.integration
@pytest.mark.asyncio
async def test_llm_completion():
    """Test LLM completion."""
    response = await client.chat_completion(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}],
    )
    assert response is not None
```

**Orchestration Test Example**:
```python
import pytest
from src.agents.base_agent import BaseAgent

@pytest.mark.orchestration
@pytest.mark.asyncio
async def test_multi_agent_collaboration():
    """Test multiple agents working together."""
    # Test implementation
    pass
```

### Test Coverage

```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html

# View report
open htmlcov/index.html
```

## Project Structure

```
rag7/
├── .github/
│   └── workflows/           # CI/CD workflows
├── deploy/                  # Deployment configurations
│   ├── cloud-run/
│   ├── gke/
│   ├── vertex-ai/
│   └── terraform/
├── docs/                    # Documentation
├── monitoring/              # Monitoring configs
│   ├── grafana-dashboards/
│   └── prometheus-config.yml
├── src/                     # Source code
│   ├── agents/              # Agent implementations
│   ├── llm/                 # LLM integration
│   ├── observability/       # Metrics, tracing, logging
│   ├── config.py            # Configuration
│   └── main.py              # Application entry point
├── tests/                   # Tests
│   ├── unit/
│   ├── integration/
│   ├── orchestration/
│   ├── load/
│   └── e2e/
├── docker-compose.yml       # Local development
├── Dockerfile               # Container definition
├── Makefile                 # Development commands
├── pyproject.toml           # Python project config
├── requirements.txt         # Production dependencies
└── requirements-dev.txt     # Development dependencies
```

## Creating New Agents

### 1. Define Agent Class

Create a new file in `src/agents/`:

```python
"""My custom agent implementation."""
from typing import Any, Dict
from .base_agent import BaseAgent

class MyAgent(BaseAgent):
    """Custom agent for specific task."""
    
    def __init__(self):
        super().__init__(
            name="my_agent",
            description="Agent that does something specific"
        )
    
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task.
        
        Args:
            task: Task data with 'type' and other fields
            
        Returns:
            Result dictionary
        """
        # Use LLM if needed
        response = await self.query_llm(
            prompt=f"Process this task: {task.get('data')}",
            model="gpt-4-turbo"
        )
        
        return {
            "status": "completed",
            "result": response
        }
```

### 2. Add Tests

Create `tests/unit/test_my_agent.py`:

```python
import pytest
from src.agents.my_agent import MyAgent

@pytest.mark.unit
@pytest.mark.asyncio
async def test_my_agent_process():
    """Test agent processing."""
    agent = MyAgent()
    task = {"id": "test", "type": "analysis", "data": "test data"}
    
    result = await agent.execute_task(task)
    
    assert result["status"] == "completed"
    assert "result" in result
```

### 3. Register Agent

Add to agent registry in `src/agents/__init__.py`:

```python
from .my_agent import MyAgent

AGENT_REGISTRY = {
    "my_agent": MyAgent,
    # ... other agents
}
```

## Debugging

### Local Debugging

**With VS Code**:

Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "src.main:app",
                "--reload",
                "--host", "0.0.0.0",
                "--port", "8080"
            ],
            "jinja": true,
            "justMyCode": false
        }
    ]
}
```

**With iPDB**:
```python
import ipdb; ipdb.set_trace()
```

### Viewing Logs

```bash
# Docker logs
docker-compose logs -f agent-api

# All services
docker-compose logs -f
```

### Metrics and Tracing

Access local monitoring:
- Prometheus: http://localhost:9091
- Grafana: http://localhost:3000 (admin/admin)
- Jaeger: http://localhost:16686

## Common Tasks

### Adding a New Dependency

1. Add to `requirements.txt` or `requirements-dev.txt`
2. Install: `pip install -r requirements.txt`
3. Update Docker image: `make docker-build`

### Database Migrations

```bash
# Create migration (when using Alembic)
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Updating Documentation

Documentation is in Markdown format in `docs/`:
- `ARCHITECTURE.md` - System design
- `DEPLOYMENT.md` - Deployment guides
- `DEVELOPMENT.md` - This file
- `TROUBLESHOOTING.md` - Common issues

## Code Style Guidelines

### Python

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use docstrings (Google style)

**Example**:
```python
def process_data(data: Dict[str, Any], limit: int = 100) -> List[str]:
    """Process input data and return results.
    
    Args:
        data: Input data dictionary
        limit: Maximum number of results
        
    Returns:
        List of processed results
        
    Raises:
        ValueError: If data is invalid
    """
    pass
```

### Imports

```python
# Standard library
import os
import sys

# Third party
import pytest
from fastapi import FastAPI

# Local
from src.config import settings
from src.llm import client
```

### Naming Conventions

- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

## Git Workflow

### Branch Naming

- Feature: `feature/description`
- Bug fix: `bugfix/description`
- Hot fix: `hotfix/description`

### Commit Messages

Follow conventional commits:
```
feat: add new agent type
fix: resolve memory leak in LLM client
docs: update deployment guide
test: add chaos tests for agent resilience
```

### Pull Requests

1. Create feature branch
2. Make changes and commit
3. Push and create PR
4. Wait for CI checks
5. Address review comments
6. Merge when approved

## Performance Optimization

### Profiling

```bash
# Profile code
python -m cProfile -o profile.stats src/main.py

# Analyze with snakeviz
snakeviz profile.stats
```

### Load Testing

```bash
# Run Locust
locust -f tests/load/locustfile.py --host=http://localhost:8080
```

## Troubleshooting

Common issues:

**Import errors**:
```bash
# Ensure src is in PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

**Port already in use**:
```bash
# Find and kill process
lsof -i :8080
kill -9 PID
```

**Database connection errors**:
```bash
# Check if services are running
docker-compose ps

# Restart services
docker-compose restart postgres redis
```

---

For deployment information, see [DEPLOYMENT.md](DEPLOYMENT.md).
For architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md).
