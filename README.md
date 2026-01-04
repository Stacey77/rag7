# Ragamuffin

<img src="https://via.placeholder.com/800x400?text=Ragamuffin+UI+Inspiration" alt="Ragamuffin UI Inspiration" />

A full-stack AI development platform combining LangFlow, FastAPI, React, and LangGraph.

## Quick Start

### Development

```bash
# Start all services
./start-dev.sh

# Access the application
# Frontend: http://localhost:8080
# Backend API: http://localhost:8000
# LangFlow: http://localhost:7860
# LangGraph: http://localhost:7878
```

### Production

```bash
# Configure environment
cp .env.production.example .env.production
# Edit .env.production with your settings

# Generate secure keys
openssl rand -hex 32  # Use for SECRET_KEY
openssl rand -hex 32  # Use for JWT_SECRET

# Start production services
./start-prod.sh
```

## Documentation

- [README_MONOREPO.md](./README_MONOREPO.md) - Detailed overview and architecture
- [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md) - Complete production deployment guide
- [PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md) - Pre-deployment security checklist
- [RUN_COMMANDS.md](./RUN_COMMANDS.md) - Development commands

## Production Features

✅ JWT Authentication  
✅ Environment-based configuration  
✅ SSL/TLS support  
✅ Rate limiting  
✅ Health checks  
✅ Production-optimized Docker images  
✅ Nginx reverse proxy configuration  
✅ Security hardening guidelines