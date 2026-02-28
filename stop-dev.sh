#!/bin/bash
# Epic Platform - Development Shutdown Script
# This script stops all services in the Epic Platform

set -e

echo "🛑 Stopping Epic Platform services..."
echo ""

# Stop all services
docker-compose down

echo ""
echo "✅ All services stopped successfully!"
echo ""
echo "💡 To remove volumes and data, use: docker-compose down -v"
echo "🚀 To start again, use: ./start-dev.sh"
echo ""
