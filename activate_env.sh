#!/bin/bash
# Greek Conjugator Master Environment Setup
# Run this script from the project root to activate venv and start backend

echo "🚀 Greek Conjugator - Master Environment"
echo "========================================"

# Activate the master virtual environment
source venv/bin/activate

echo "✅ Virtual environment activated: $VIRTUAL_ENV"
echo "📦 Python version: $(python --version)"
echo "📍 Current directory: $(pwd)"

# Function to start backend
start_backend() {
    echo ""
    echo "🔧 Starting Flask Backend Server..."
    cd greek-conjugator/backend
    python3 run_backend.py
}

# Function to start frontend (for later use)
start_frontend() {
    echo ""
    echo "⚛️  Starting React Frontend..."
    cd greek-conjugator/frontend
    npm start
}

# Function to show help
show_help() {
    echo ""
    echo "Available commands:"
    echo "  backend   - Start the Flask backend server"
    echo "  frontend  - Start the React frontend (requires npm install first)"
    echo "  both      - Start both backend and frontend"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./activate_env.sh backend"
    echo "  ./activate_env.sh frontend"
    echo "  ./activate_env.sh both"
}

# Handle command line arguments
case "$1" in
    "backend")
        start_backend
        ;;
    "frontend")
        start_frontend
        ;;
    "both")
        echo "Starting both backend and frontend..."
        start_backend &
        start_frontend
        ;;
    "help"|"")
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        show_help
        ;;
esac
