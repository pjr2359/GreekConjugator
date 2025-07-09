# Backend Setup Instructions

## ❌ Current Issue
The Flask backend cannot start because Flask is not installed and we don't have pip access.

## ✅ Fixed Import Paths
I've already fixed the import paths in:
- `run_backend.py`: Changed `from backend.app import create_app` → `from app import create_app`
- `seed_db.py`: Fixed imports to use relative paths

## 🛠️ Setup Solutions

### Option 1: Install Flask System-wide (Recommended)
```bash
# Install Python pip first
sudo apt update
sudo apt install python3-pip

# Install Flask and dependencies
pip3 install Flask Flask-SQLAlchemy Flask-CORS Flask-Session Werkzeug python-dotenv

# Then run the server
cd /home/pjrei/greek-conjugator/greek-conjugator/backend
python3 run_backend.py
```

### Option 2: Use Virtual Environment
```bash
cd /home/pjrei/greek-conjugator/greek-conjugator/backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
python run_backend.py
```

### Option 3: Use the Simple Server (No Flask Required)
I've created a simple HTTP server that doesn't require Flask:

```bash
cd /home/pjrei/greek-conjugator/greek-conjugator/backend
python3 simple_server.py
```

This server provides:
- ✅ User registration and login
- ✅ Session management
- ✅ SQLite database
- ✅ CORS support for React frontend
- ✅ Same API endpoints as Flask version

## 🎯 What Each Option Provides

### Flask Server (Option 1 & 2)
- ✅ Full Greek text processing API
- ✅ Verb practice sessions
- ✅ Spaced repetition
- ✅ Complete feature set

### Simple Server (Option 3)
- ✅ User authentication (login/register)
- ✅ Basic session management
- ❌ No verb practice features yet
- ❌ No Greek text processing API

## 🚀 Quick Start with Simple Server

1. **Start the server:**
```bash
cd /home/pjrei/greek-conjugator/greek-conjugator/backend
python3 simple_server.py
```

2. **Start the frontend:**
```bash
cd /home/pjrei/greek-conjugator/greek-conjugator/frontend
npm start
```

3. **Test authentication:**
- Go to http://localhost:3000
- Try registering a new account
- Try logging in

## 📝 Next Steps

If the simple server works for authentication, I can extend it to include:
1. Verb practice endpoints
2. Greek text processing
3. Spaced repetition functionality

The simple server uses only Python standard library, so it should work without any package installation!