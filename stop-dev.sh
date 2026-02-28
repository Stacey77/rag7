#!/bin/bash

# Epic Platform - Stop Development Environment
# This script stops all services using docker compose

set -e

echo "🛑 Stopping Epic Platform Development Environment..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "⚠️  Warning: Docker is not running."
    exit 0
fi

# Stop services
docker compose down

echo ""
echo "✅ All services stopped"
echo ""
echo "💡 To remove volumes and data:"
echo "  docker compose down -v"
echo ""
echo "🚀 To start again:"
echo "  ./start-dev.sh"
echo ""
