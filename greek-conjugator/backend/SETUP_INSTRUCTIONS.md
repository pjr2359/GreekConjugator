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

## ✅ Verify Your Setup

After installing dependencies choose one of the following quick checks:

```bash
# Smoke-test the Flask API
python3 run_backend.py

# In a separate terminal, run the focused text processing test suite
python3 test_greek_processing.py
```

Both commands must be executed from `/home/pjrei/greek-conjugator/greek-conjugator/backend`.

## 📝 Next Steps

- Seed the development database if you need sample data:
  ```bash
  python3 seed_db.py
  ```
- Run the frontend from `frontend/` with `npm start` and sign in through the React app.
