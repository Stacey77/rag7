#!/bin/bash

# Epic Platform - Stop Development Environment
# This script stops all services and cleans up containers

echo "🛑 Stopping Epic Platform..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    exit 1
fi

# Stop and remove containers
echo "🔄 Stopping services..."
docker-compose down

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Epic Platform stopped successfully!"
    echo ""
    echo "💡 To also remove volumes (data), use: docker-compose down -v"
    echo "💡 To remove images as well, use: docker-compose down --rmi all"
else
    echo ""
    echo "❌ Failed to stop services"
    echo "Try manually with: docker-compose down"
    exit 1
fi
