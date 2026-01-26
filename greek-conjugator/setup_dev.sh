#!/bin/bash

echo "🚀 Greek Conjugator - Local Development Setup"
echo "============================================="

# Check if we're in the right directory
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo "❌ Please run this script from the greek-conjugator directory"
    exit 1
fi

echo "📦 Installing frontend dependencies..."
(cd frontend && npm install)

echo "🐍 Setting up root Python virtual environment..."
if [ ! -d "../venv" ]; then
    (cd .. && python3 -m venv venv)
fi

echo "📦 Installing backend dependencies into root venv..."
(cd backend && source ../venv/bin/activate && pip install -r requirements.txt)

echo "✅ Setup complete!"
echo ""
echo "🎯 To run the application, use the start_dev.sh script"
echo ""
echo "📱 The app will be available at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:5000"