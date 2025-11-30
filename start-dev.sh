#!/bin/bash

# Epic Platform - Start Development Environment
# This script starts all services using docker compose

set -e

echo "🚀 Starting Epic Platform Development Environment..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker compose is available
if ! docker compose version > /dev/null 2>&1; then
    echo "❌ Error: Docker Compose is not available. Please install Docker Compose v2+."
    exit 1
fi

# Create flows directory if it doesn't exist
mkdir -p ./langflow-backend/flows
echo "✅ Flows directory ready"

# Start services
echo ""
echo "📦 Building and starting services..."
docker compose up -d --build

# Wait a moment for services to initialize
echo ""
echo "⏳ Waiting for services to initialize..."
sleep 5

# Check service status
echo ""
echo "🔍 Service Status:"
docker compose ps

# Display access URLs
echo ""
echo "✅ Epic Platform is ready!"
echo ""
echo "🌐 Access URLs:"
echo "  - LangFlow:    http://localhost:7860"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs:    http://localhost:8000/docs"
echo "  - Frontend:    http://localhost:8080"
echo ""
echo "📊 View logs:"
echo "  docker compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "  ./stop-dev.sh"
echo ""
