#!/usr/bin/env python3
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Starting Flask backend on http://localhost:5000")
    print("📊 Using SQLite database for local development")
    app.run(debug=True, host='0.0.0.0', port=5000)