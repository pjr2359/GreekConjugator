#!/bin/bash
echo "🧪 Testing Greek Conjugator Login System"
echo "========================================"

# Test if backend is running
echo "1. Checking if backend is running..."
if curl -s http://localhost:5000/api/auth/check > /dev/null; then
    echo "   ✅ Backend is running on port 5000"
else
    echo "   ❌ Backend is not running"
    echo "   💡 Start with: cd backend && python run_backend.py"
    exit 1
fi

echo ""
echo "2. Testing registration endpoint..."
response=$(curl -s -w "\nSTATUS:%{http_code}" -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"debug@test.com","username":"debuguser","password":"test123"}')

echo "   Response: $response"

echo ""
echo "3. Testing login endpoint..."
response=$(curl -s -w "\nSTATUS:%{http_code}" -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"debug@test.com","password":"test123"}')

echo "   Response: $response"

echo ""
echo "4. Testing auth check endpoint..."
response=$(curl -s -w "\nSTATUS:%{http_code}" http://localhost:5000/api/auth/check)
echo "   Response: $response"

echo ""
echo "🎯 Test completed!"
echo "   If you see STATUS:200 or STATUS:201, the API is working"
echo "   If you see STATUS:404 or STATUS:500, there's a backend issue"
echo "   If you see connection errors, the Flask server isn't running"