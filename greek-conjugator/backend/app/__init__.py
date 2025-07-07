from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_session import Session
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, static_folder='../../frontend/build')
    CORS(app, supports_credentials=True)

    # Use SQLite for local development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///greek_conjugator_dev.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # Session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'greek_conjugator:'
    Session(app)

    # Initialize database
    from .models import db
    db.init_app(app)

    # Register blueprints
    from .routes import auth, verbs, text_validation
    app.register_blueprint(auth.bp)
    app.register_blueprint(verbs.bp)
    app.register_blueprint(text_validation.bp)

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    # Serve React app for SPA routing
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react_app(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)