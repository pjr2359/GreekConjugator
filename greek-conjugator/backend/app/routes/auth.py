from flask import Blueprint, request, jsonify, session
from ..models import db, User
from datetime import datetime
from functools import wraps

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400

        if username and User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already taken'}), 400

        new_user = User(
            email=email,
            username=username,
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'success': True, 'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': 'Registration failed'}), 500

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['subscription_tier'] = user.subscription_tier

            user.last_login = datetime.utcnow()
            db.session.commit()

            return jsonify({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'subscription_tier': user.subscription_tier
                }
            })

        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500

@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({'success': True})

@bp.route('/check', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'subscription_tier': user.subscription_tier
                }
            })
    return jsonify({'authenticated': False})

@bp.route('/reset-password', methods=['POST'])
def reset_password():
    # Placeholder for password reset functionality
    return jsonify({'message': 'Password reset functionality to be implemented'}), 501