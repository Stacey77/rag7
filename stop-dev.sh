#!/bin/bash

# Ragamuffin Platform - Stop Development Environment
# This script stops all services

echo "🛑 Stopping Ragamuffin Platform..."
echo "=================================="

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    exit 1
fi

# Stop services
docker-compose down

echo ""
echo "=================================="
echo "✓ Ragamuffin Platform stopped!"
echo ""
echo "To restart: ./start-dev.sh"
echo "To remove volumes: docker-compose down -v"
