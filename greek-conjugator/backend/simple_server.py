#!/usr/bin/env python3
"""
Simple HTTP server for Greek Conjugator authentication
This is a minimal implementation that doesn't require Flask installation
"""

import json
import sqlite3
import hashlib
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import uuid
import time

# Simple database setup
DB_PATH = 'greek_conjugator_dev.db'

def init_database():
    """Initialize SQLite database with basic tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT,
            password_hash TEXT NOT NULL,
            subscription_tier TEXT DEFAULT 'free',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Create sessions table for simple session management
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hash_password(password) == password_hash

def create_session(user_id):
    """Create a new session for user"""
    session_id = str(uuid.uuid4())
    expires_at = time.time() + (24 * 60 * 60)  # 24 hours
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)",
        (session_id, user_id, expires_at)
    )
    conn.commit()
    conn.close()
    
    return session_id

def get_user_from_session(session_id):
    """Get user from session ID"""
    if not session_id:
        return None
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.email, u.username, u.subscription_tier 
        FROM users u 
        JOIN sessions s ON u.id = s.user_id 
        WHERE s.session_id = ? AND s.expires_at > ?
    ''', (session_id, time.time()))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'id': result[0],
            'email': result[1],
            'username': result[2],
            'subscription_tier': result[3]
        }
    return None

class GreekConjugatorHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:3000')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()

    def do_POST(self):
        """Handle POST requests"""
        self.send_cors_headers()
        
        path = urlparse(self.path).path
        
        if path == '/api/auth/register':
            self.handle_register()
        elif path == '/api/auth/login':
            self.handle_login()
        elif path == '/api/auth/logout':
            self.handle_logout()
        else:
            self.send_error(404, "Not Found")

    def do_GET(self):
        """Handle GET requests"""
        self.send_cors_headers()
        
        path = urlparse(self.path).path
        
        if path == '/api/auth/check':
            self.handle_auth_check()
        else:
            self.send_error(404, "Not Found")

    def send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:3000')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Content-Type', 'application/json')

    def handle_register(self):
        """Handle user registration"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            email = data.get('email')
            username = data.get('username')
            password = data.get('password')
            
            if not email or not password:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Email and password are required'}).encode())
                return
            
            # Check if user already exists
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            
            if cursor.fetchone():
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Email already registered'}).encode())
                conn.close()
                return
            
            # Create new user
            password_hash = hash_password(password)
            cursor.execute(
                "INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)",
                (email, username, password_hash)
            )
            conn.commit()
            conn.close()
            
            self.send_response(201)
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'message': 'User registered successfully'}).encode())
            
        except Exception as e:
            print(f"Registration error: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Registration failed'}).encode())

    def handle_login(self):
        """Handle user login"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            email = data.get('email')
            password = data.get('password')
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, username, password_hash, subscription_tier FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            conn.close()
            
            if user and verify_password(password, user[3]):
                # Create session
                session_id = create_session(user[0])
                
                # Update last login
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user[0],))
                conn.commit()
                conn.close()
                
                self.send_response(200)
                self.send_header('Set-Cookie', f'session_id={session_id}; Path=/; HttpOnly; SameSite=Lax')
                self.end_headers()
                
                response = {
                    'success': True,
                    'user': {
                        'id': user[0],
                        'email': user[1],
                        'username': user[2],
                        'subscription_tier': user[4]
                    }
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(401)
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid credentials'}).encode())
                
        except Exception as e:
            print(f"Login error: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Login failed'}).encode())

    def handle_logout(self):
        """Handle user logout"""
        try:
            # Get session from cookie
            cookies = self.headers.get('Cookie', '')
            session_id = None
            
            for cookie in cookies.split(';'):
                if 'session_id=' in cookie:
                    session_id = cookie.split('session_id=')[1].strip()
                    break
            
            if session_id:
                # Delete session
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                conn.commit()
                conn.close()
            
            self.send_response(200)
            self.send_header('Set-Cookie', 'session_id=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
            
        except Exception as e:
            print(f"Logout error: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Logout failed'}).encode())

    def handle_auth_check(self):
        """Handle authentication check"""
        try:
            # Get session from cookie
            cookies = self.headers.get('Cookie', '')
            session_id = None
            
            for cookie in cookies.split(';'):
                if 'session_id=' in cookie:
                    session_id = cookie.split('session_id=')[1].strip()
                    break
            
            user = get_user_from_session(session_id)
            
            if user:
                self.send_response(200)
                self.end_headers()
                response = {
                    'authenticated': True,
                    'user': user
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'authenticated': False}).encode())
                
        except Exception as e:
            print(f"Auth check error: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Auth check failed'}).encode())

    def log_message(self, format, *args):
        """Override to reduce log noise"""
        if "OPTIONS" not in format:
            print(f"{self.address_string()} - {format % args}")

def main():
    print("🚀 Starting Greek Conjugator Simple Server")
    print("=" * 50)
    
    # Initialize database
    init_database()
    
    # Start server
    server_address = ('localhost', 5000)
    httpd = HTTPServer(server_address, GreekConjugatorHandler)
    
    print("✅ Server running on http://localhost:5000")
    print("📊 Using SQLite database for authentication")
    print("🔄 CORS enabled for http://localhost:3000")
    print("Press Ctrl+C to stop...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.server_close()

if __name__ == '__main__':
    main()