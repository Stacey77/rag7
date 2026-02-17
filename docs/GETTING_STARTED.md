# Getting Started with RAG7

## Quick Start Guide

This guide will help you set up and run the RAG7 AI Platform in minutes.

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Stacey77/rag7.git
cd rag7
```

### 2. Run Setup Script

The easiest way to get started:

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This script will:
- Check Python version
- Create virtual environment
- Install dependencies
- Create `.env` file from template
- Set up necessary directories

### 3. Configure API Keys

Edit the `.env` file with your API keys:

```bash
nano .env  # or use your preferred editor
```

Add your API keys:
```
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 4. Start the Server

```bash
source venv/bin/activate  # Activate virtual environment
python -m app.main
```

The server will start on http://localhost:8000

### 5. Access the Platform

- **Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Docker Quick Start

If you prefer Docker:

```bash
# Copy environment file
cp .env.example .env

# Edit with your API keys
nano .env

# Start with Docker Compose
docker-compose up -d
```

Access at http://localhost:8000

## First Steps

### 1. Test the API

```bash
# Check health
curl http://localhost:8000/health

# List LLM providers
curl http://localhost:8000/api/v1/llm/providers

# List agent types
curl http://localhost:8000/api/v1/agents/types
```

### 2. Create Your First Project

Using the dashboard:
1. Navigate to the Projects tab
2. Click "New Project"
3. Fill in project details
4. Submit

Or via API:
```bash
curl -X POST "http://localhost:8000/api/v1/projects/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First AI Project",
    "description": "Testing the platform",
    "use_case": "general",
    "llm_providers": ["openai"]
  }'
```

### 3. Generate Your First Completion

Using the LLM Console in the dashboard:
1. Navigate to LLM Console tab
2. Select provider (OpenAI or Anthropic)
3. Enter a prompt
4. Click Generate

Or via API:
```bash
curl -X POST "http://localhost:8000/api/v1/llm/completion" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms",
    "provider": "openai",
    "temperature": 0.7
  }'
```

### 4. Execute an AI Agent

From the Agents tab in the dashboard:
1. Select an agent type
2. Enter task instruction
3. Click Execute

Or via API:
```bash
curl -X POST "http://localhost:8000/api/v1/agents/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "research",
    "instruction": "Research latest AI trends",
    "max_iterations": 5
  }'
```

## Common Tasks

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Stopping the Server

- If running directly: Press `Ctrl+C`
- If running with Docker: `docker-compose down`

### Viewing Logs

- **Direct run**: Logs appear in console and `logs/` directory
- **Docker**: `docker-compose logs -f`

### Updating Dependencies

```bash
pip install -r requirements.txt --upgrade
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

```bash
# Change port in .env
API_PORT=8001

# Or specify when running
python -m app.main --port 8001
```

### API Key Errors

If you see "API key not initialized" errors:

1. Check `.env` file has correct API keys
2. Restart the server
3. Verify keys are valid

### Import Errors

If you see "No module named 'app'" errors:

```bash
# Make sure you're in the project root
cd /path/to/rag7

# Run with PYTHONPATH
PYTHONPATH=/path/to/rag7 python -m app.main
```

### Docker Issues

```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# View logs
docker-compose logs -f api
```

## Next Steps

- Read the [API Documentation](./API.md) for detailed API reference
- Check [Architecture](./ARCHITECTURE.md) to understand the system design
- Review [Deployment Guide](./DEPLOYMENT.md) for production deployment
- Explore example projects in the dashboard

## Getting Help

- **Documentation**: Check the `docs/` directory
- **Issues**: Open an issue on GitHub
- **API Docs**: Visit http://localhost:8000/docs for interactive API documentation

## Configuration Options

Key environment variables you can configure:

```bash
# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_ENV=development

# LLM Providers
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key

# Database
DATABASE_URL=sqlite:///./rag7.db

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Features
ENABLE_METRICS=true
ENABLE_TRACING=true
```

See `.env.example` for complete list of options.

## Development Mode

For development with auto-reload:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Production Considerations

Before deploying to production:

1. ✅ Change `SECRET_KEY` in `.env`
2. ✅ Set `API_ENV=production`
3. ✅ Use managed databases (PostgreSQL, Redis)
4. ✅ Set up proper authentication
5. ✅ Configure SSL/TLS
6. ✅ Set up monitoring and alerting
7. ✅ Review security settings

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed production deployment guide.

## Resources

- **GitHub Repository**: https://github.com/Stacey77/rag7
- **API Documentation**: http://localhost:8000/docs
- **Project Homepage**: http://localhost:8000

---

**Welcome to RAG7!** Start building powerful AI products today. 🚀
