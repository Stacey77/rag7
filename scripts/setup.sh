#!/bin/bash

# RAG7 Platform Setup Script
# This script sets up the RAG7 AI platform for local development

set -e

echo "🚀 Setting up RAG7 AI Platform..."
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
if [ "$(printf '%s\n' "3.11" "$python_version" | sort -V | head -n1)" != "3.11" ]; then
    echo "❌ Python 3.11 or higher is required. Found: $python_version"
    exit 1
fi
echo "✅ Python version: $python_version"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Setup environment file
echo "⚙️  Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "⚠️  Please edit .env with your API keys and configuration"
else
    echo "✅ .env file already exists"
fi
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs data/raw data/processed
echo "✅ Directories created"
echo ""

# Run health check
echo "🏥 Running health check..."
python -c "from app.core.config import settings; print('✅ Configuration loaded successfully')"
echo ""

echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python -m app.main"
echo "4. Access API at: http://localhost:8000"
echo "5. View docs at: http://localhost:8000/docs"
echo ""
