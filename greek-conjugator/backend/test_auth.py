#!/usr/bin/env python3
"""
Test script to verify authentication is working
"""

import sys
import os
import requests
import json

# Test the authentication endpoints
def test_auth():
    base_url = "http://localhost:5000/api"
    
    print("🧪 Testing Authentication Endpoints")
    print("=" * 40)
    
    # Test data
    test_user = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        # Test registration
        print("\n1. Testing Registration...")
        response = requests.post(
            f"{base_url}/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("   ✅ Registration working")
        elif response.status_code == 400 and "already registered" in response.text:
            print("   ✅ Registration working (user already exists)")
        else:
            print("   ❌ Registration failed")
            return False
        
        # Test login
        print("\n2. Testing Login...")
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        session = requests.Session()
        response = session.post(
            f"{base_url}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Login working")
            
            # Test authenticated endpoint
            print("\n3. Testing Auth Check...")
            response = session.get(f"{base_url}/auth/check")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 200:
                print("   ✅ Auth check working")
                return True
            else:
                print("   ❌ Auth check failed")
                return False
        else:
            print("   ❌ Login failed")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("   Make sure the Flask server is running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_auth()
    if success:
        print("\n🎯 All authentication tests passed!")
    else:
        print("\n💥 Authentication tests failed!")
        print("   Check that the backend server is running and accessible")
    
    sys.exit(0 if success else 1)