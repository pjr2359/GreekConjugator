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

echo "🐍 Setting up Python virtual environment..."
(cd backend && python3 -m venv venv)

echo "📦 Installing backend dependencies..."
(cd backend && source venv/bin/activate && pip install -r requirements.txt)

echo "🌱 Setting up database and seeding data..."
(cd backend && source venv/bin/activate && python3 seed_db.py)

echo "✅ Setup complete!"
echo ""
echo "🎯 To run the application, use the start_dev.sh script"
echo ""
echo "📱 The app will be available at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:5000"