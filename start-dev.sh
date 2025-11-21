#!/bin/bash

# Ragamuffin Platform - Start Development Environment
# This script starts all services using Docker Compose

echo "🚀 Starting Ragamuffin Platform..."
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    exit 1
fi

# Create flows directory if it doesn't exist
mkdir -p langflow-backend/flows
echo "✓ Flows directory ready"

# Start services
echo ""
echo "Building and starting services..."
echo "This may take a few minutes on first run..."
echo ""

docker-compose up --build

echo ""
echo "=================================="
echo "✓ Ragamuffin Platform started!"
echo ""
echo "Access points:"
echo "  • Frontend:  http://localhost:8080"
echo "  • Backend:   http://localhost:8000"
echo "  • API Docs:  http://localhost:8000/docs"
echo "  • LangFlow:  http://localhost:7860"
echo ""
echo "Press Ctrl+C to stop all services"
echo "Or run ./stop-dev.sh in another terminal"
