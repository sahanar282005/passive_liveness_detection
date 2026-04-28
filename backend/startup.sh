#!/bin/bash

# PassiveLiveness API - Startup Script
# This script sets up and runs the backend

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     PassiveLiveness API - Backend Startup Script           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Check if dependencies are installed
echo ""
echo "Verifying setup..."
python3 verify_setup.py

# Check exit code from verification
if [ $? -ne 0 ]; then
    echo ""
    echo "Setup verification failed. Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  Starting API Server                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "API will be available at: http://localhost:8000"
echo "Documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Start the server
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
