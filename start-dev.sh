#!/bin/bash

# Epic Platform - Start Development Environment
# This script starts all services using Docker Compose

echo "🚀 Starting Epic Platform..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "Please install Docker Compose and try again"
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check for port conflicts
echo "🔍 Checking for port conflicts..."
PORTS_IN_USE=""

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    PORTS_IN_USE="$PORTS_IN_USE 3000"
fi

if lsof -Pi :7860 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    PORTS_IN_USE="$PORTS_IN_USE 7860"
fi

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    PORTS_IN_USE="$PORTS_IN_USE 8000"
fi

if [ -n "$PORTS_IN_USE" ]; then
    echo "⚠️  Warning: The following ports are already in use:$PORTS_IN_USE"
    echo "Please stop the services using these ports or modify docker-compose.yml"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Ports are available"
echo ""

# Build and start services
echo "🏗️  Building and starting services..."
echo "This may take a few minutes on first run..."
echo ""

docker-compose up --build -d

# Check if services started successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Epic Platform started successfully!"
    echo ""
    echo "📍 Access the services at:"
    echo "   - Frontend:  http://localhost:3000"
    echo "   - Backend:   http://localhost:8000 (API docs: http://localhost:8000/docs)"
    echo "   - LangFlow:  http://localhost:7860"
    echo ""
    echo "📋 Useful commands:"
    echo "   - View logs:        docker-compose logs -f"
    echo "   - Stop services:    ./stop-dev.sh"
    echo "   - Restart service:  docker-compose restart <service-name>"
    echo ""
    echo "⏳ Services are starting up... Please wait a moment before accessing."
    echo "   You can monitor the startup with: docker-compose logs -f"
else
    echo ""
    echo "❌ Failed to start services"
    echo "Check the logs with: docker-compose logs"
    exit 1
fi
