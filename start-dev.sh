#!/bin/bash

# Ragamuffin Development Environment - Start Script
# This script starts all Ragamuffin services using Docker Compose

set -e

echo "🎸 Starting Ragamuffin development environment..."
echo ""

# Build and start all services
docker compose up -d --build

echo ""
echo "✅ Ragamuffin services started successfully!"
echo ""
echo "📦 Services:"
echo "  - LangFlow:  http://localhost:7860"
echo "  - Backend:   http://localhost:8000"
echo "  - Frontend:  http://localhost:8080"
echo ""
echo "📊 View logs with: docker compose logs -f"
echo "🛑 Stop with: ./stop-dev.sh"
echo ""
