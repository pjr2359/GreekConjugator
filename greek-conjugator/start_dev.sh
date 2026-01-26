#!/bin/bash

echo "🚀 Starting Greek Conjugator Development Environment"
echo "=================================================="

# Check if we're in the right directory
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo "❌ Please run this script from the greek-conjugator directory"
    exit 1
fi

# Function to handle cleanup when script is terminated
cleanup() {
    echo ""
    echo "🛑 Shutting down development servers..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set up trap to catch Ctrl+C and cleanup background processes
trap cleanup SIGINT SIGTERM

echo "🐍 Starting Flask backend..."
if [ -f "../venv/bin/activate" ]; then
    echo "   Using root venv"
    (cd backend && source ../venv/bin/activate && python3 run_backend.py) &
else
    echo "❌ Root venv not found at ../venv. Please create/activate it first."
    exit 1
fi
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

echo "⚛️  Starting React frontend..."
(cd frontend && npm start) &
FRONTEND_PID=$!

echo ""
echo "✅ Both servers are starting up!"
echo "📱 Your application will be available at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:5000"
echo ""
echo "🔄 Watching for changes... Press Ctrl+C to stop both servers"

# Wait for both background processes
wait