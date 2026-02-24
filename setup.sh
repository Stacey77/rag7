#!/bin/bash

# RAG7 AI Agent Platform - Quick Setup Script
# This script helps you get started quickly

set -e  # Exit on error

echo "🤖 RAG7 AI Agent Platform - Quick Setup"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env file${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY${NC}"
    echo "   You can get one from: https://platform.openai.com/api-keys"
    echo ""
    read -p "Press Enter after you've added your OPENAI_API_KEY to .env..."
fi

# Check for required tools
echo "Checking requirements..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    echo "Please install Python 3.11 or higher"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"

# Check Node
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found${NC}"
    echo "Please install Node.js 18 or higher"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✅ Node $NODE_VERSION${NC}"

# Check Docker (optional)
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
    echo -e "${GREEN}✅ Docker $DOCKER_VERSION${NC}"
    DOCKER_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  Docker not found (optional)${NC}"
    DOCKER_AVAILABLE=false
fi

echo ""
echo "Choose setup method:"
echo "1) Docker Compose (Recommended - runs everything)"
echo "2) Manual Setup (Backend + Frontend separately)"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        if [ "$DOCKER_AVAILABLE" = false ]; then
            echo -e "${RED}❌ Docker not available. Please install Docker or choose option 2${NC}"
            exit 1
        fi
        
        echo ""
        echo "🐳 Starting with Docker Compose..."
        echo "This will:"
        echo "  - Build backend and frontend Docker images"
        echo "  - Start Redis and ChromaDB"
        echo "  - Start API server on port 8000"
        echo "  - Start frontend on port 3000"
        echo ""
        
        docker-compose up --build
        ;;
        
    2)
        echo ""
        echo "🔧 Manual Setup"
        echo ""
        
        # Backend setup
        echo "📦 Installing Python dependencies..."
        pip3 install -q -r requirements.txt
        echo -e "${GREEN}✅ Python dependencies installed${NC}"
        echo ""
        
        # Frontend setup
        echo "📦 Installing Node dependencies..."
        cd frontend
        npm install --silent
        cd ..
        echo -e "${GREEN}✅ Node dependencies installed${NC}"
        echo ""
        
        # Start services
        echo "🚀 Starting services..."
        echo ""
        echo "Backend will start on: http://localhost:8000"
        echo "Frontend will start on: http://localhost:3000"
        echo ""
        echo "Press Ctrl+C to stop both servers"
        echo ""
        
        # Start backend in background
        echo "Starting backend..."
        uvicorn src.interfaces.web_api:app --reload --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
        
        # Give backend time to start
        sleep 3
        
        # Start frontend
        echo "Starting frontend..."
        cd frontend
        npm start &
        FRONTEND_PID=$!
        cd ..
        
        # Trap Ctrl+C to kill both processes
        trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
        
        # Wait for both processes
        wait $BACKEND_PID $FRONTEND_PID
        ;;
        
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Access the platform at:"
echo "  Frontend: http://localhost:3000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Health:   http://localhost:8000/health"
echo ""
echo "Features:"
echo "  💬 Full GUI Dashboard with navigation"
echo "  🤖 Floating Bot Widget (bottom-right corner)"
echo "  🔌 Integrations (Slack, Gmail, Notion)"
echo "  📊 Analytics and monitoring"
echo ""
echo "Next steps:"
echo "  1. Visit http://localhost:3000"
echo "  2. Try the chat interface"
echo "  3. Click the floating bot button"
echo "  4. Configure integrations in Settings"
echo ""
echo "Need help? See TROUBLESHOOTING.md"
echo ""
