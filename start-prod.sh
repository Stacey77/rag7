#!/bin/bash
# Start Ragamuffin production environment

set -e

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo "Error: .env.production file not found"
    echo "Copy .env.production.example to .env.production and configure it"
    exit 1
fi

# Check for required environment variables
source .env.production

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-secret-key-here-change-me" ]; then
    echo "Error: SECRET_KEY not configured in .env.production"
    echo "Generate one with: openssl rand -hex 32"
    exit 1
fi

if [ -z "$JWT_SECRET" ] || [ "$JWT_SECRET" = "your-jwt-secret-here-change-me" ]; then
    echo "Error: JWT_SECRET not configured in .env.production"
    echo "Generate one with: openssl rand -hex 32"
    exit 1
fi

echo "Starting Ragamuffin in production mode..."
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build

echo ""
echo "✅ Ragamuffin started successfully!"
echo ""
echo "Services:"
echo "  Frontend: http://localhost:${FRONTEND_PORT:-8080}"
echo "  Backend:  http://localhost:${BACKEND_PORT:-8000}"
echo "  LangFlow: http://localhost:${LANGFLOW_PORT:-7860}"
echo "  LangGraph: http://localhost:${LANGGRAPH_PORT:-7878}"
echo ""
echo "To view logs: docker compose -f docker-compose.prod.yml logs -f"
echo "To stop: ./stop-prod.sh"
