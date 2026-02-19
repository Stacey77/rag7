#!/bin/bash

# AGI System Startup Script

echo "=================================="
echo "AGI System - Startup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python --version

if [ $? -ne 0 ]; then
    echo "Error: Python not found. Please install Python 3.9 or higher."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi

echo ""
echo "✓ Setup complete!"
echo ""

# Ask user what to run
echo "What would you like to run?"
echo "1) Run basic usage example"
echo "2) Run emotional reasoning demo"
echo "3) Run symbolic reasoning demo"
echo "4) Start API server"
echo "5) Run tests"
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo ""
        echo "Running basic usage example..."
        python examples/basic_usage.py
        ;;
    2)
        echo ""
        echo "Running emotional reasoning demo..."
        python examples/emotional_reasoning_demo.py
        ;;
    3)
        echo ""
        echo "Running symbolic reasoning demo..."
        python examples/symbolic_reasoning_demo.py
        ;;
    4)
        echo ""
        echo "Starting API server..."
        echo "API will be available at: http://localhost:8000"
        echo "API docs at: http://localhost:8000/docs"
        echo ""
        python -m agi_system.api.rest_api
        ;;
    5)
        echo ""
        echo "Running tests..."
        pytest tests/ -v
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "=================================="
echo "Done!"
echo "=================================="
