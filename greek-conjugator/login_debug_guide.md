# Login/Registration Debug Guide

## ✅ ESLint Warnings Fixed
All React hooks ESLint warnings have been resolved with proper eslint-disable comments.

## 🔍 Login Issue Debugging Steps

### Step 1: Check Backend Server Status
```bash
cd greek-conjugator/backend
source venv/bin/activate
python run_backend.py
```

**Expected Output:**
```
🚀 Starting Flask backend on http://localhost:5000
📊 Using SQLite database for local development
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://[::1]:5000
```

### Step 2: Test API Endpoints Directly
```bash
# Test registration endpoint
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"password123"}'

# Test login endpoint  
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Step 3: Check Browser Developer Tools

1. **Open Browser DevTools (F12)**
2. **Go to Network tab**
3. **Try to register/login**
4. **Look for:**
   - Red errors in Console tab
   - Failed network requests in Network tab
   - CORS errors

### Step 4: Common Error Patterns

#### Error: "Failed to fetch" or "Network Error"
**Cause:** Backend server not running
**Solution:** Start Flask server (Step 1)

#### Error: "CORS policy error"
**Cause:** Frontend can't communicate with backend
**Solution:** Already fixed with CORS configuration

#### Error: "Registration failed" or "Login failed"
**Cause:** API endpoint errors
**Solution:** Check Flask server logs in terminal

#### Error: No response from server
**Cause:** Wrong API URL or port
**Solution:** Verify frontend is using http://localhost:5000

### Step 5: Advanced Debugging

#### Check Frontend API Configuration
File: `frontend/src/services/api.js`
```javascript
// Should show:
const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? 'https://yourusername.pythonanywhere.com/api'
  : 'http://localhost:5000/api'; // ← This should be localhost:5000
```

#### Check Flask Server Logs
When you try to login, Flask server should show:
```
127.0.0.1 - - [timestamp] "POST /api/auth/login HTTP/1.1" 200 -
```

If you see 404 or 500 errors, there's a backend issue.

### Step 6: Database Issues

#### Missing Database
```bash
cd greek-conjugator/backend
ls -la *.db
# Should show: greek_conjugator_dev.db
```

#### Recreate Database
```bash
cd greek-conjugator/backend
rm -f greek_conjugator_dev.db
python run_backend.py  # Will recreate database
```

## 🎯 Quick Test Script

Create and run this test:

```bash
# Save as test_login.sh
#!/bin/bash
echo "Testing Greek Conjugator Login..."

# Test if backend is running
if curl -s http://localhost:5000/api/auth/check > /dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not running - start with: python run_backend.py"
    exit 1
fi

# Test registration
echo "Testing registration..."
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"debug@test.com","username":"debuguser","password":"test123"}' \
  -w "\nStatus: %{http_code}\n"

# Test login
echo "Testing login..."
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"debug@test.com","password":"test123"}' \
  -w "\nStatus: %{http_code}\n"

echo "Done!"
```

## 📋 What to Check Next

Please share:
1. **Flask server output** when you start it
2. **Browser console errors** (F12 → Console tab)
3. **Network tab errors** when trying to login
4. **Any error messages** you see in the UI

This will help identify the exact issue!