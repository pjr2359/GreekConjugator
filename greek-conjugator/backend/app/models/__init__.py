from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    subscription_tier = db.Column(db.String(50), default='free')  # Changed from Enum for SQLite
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    preferences = db.Column(db.Text, nullable=True)  # Changed from JSON for SQLite

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'subscription_tier': self.subscription_tier,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'preferences': self.preferences
        }

class Verb(db.Model):
    __tablename__ = 'verbs'
    id = db.Column(db.Integer, primary_key=True)
    infinitive = db.Column(db.String(100), nullable=False)
    english = db.Column(db.String(255), nullable=False)
    frequency = db.Column(db.Integer)
    difficulty = db.Column(db.Integer)
    verb_group = db.Column(db.String(50))  # Changed from Enum for SQLite
    transitivity = db.Column(db.String(50))  # Changed from Enum for SQLite
    tags = db.Column(db.Text)  # Changed from JSON for SQLite
    audio_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'infinitive': self.infinitive,
            'english': self.english,
            'frequency': self.frequency,
            'difficulty': self.difficulty,
            'verb_group': self.verb_group,
            'transitivity': self.transitivity,
            'tags': self.tags,
            'audio_url': self.audio_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Conjugation(db.Model):
    __tablename__ = 'conjugations'
    id = db.Column(db.Integer, primary_key=True)
    verb_id = db.Column(db.Integer, db.ForeignKey('verbs.id'), nullable=False)
    tense = db.Column(db.String(50), nullable=False)  # Changed from Enum for SQLite
    mood = db.Column(db.String(50), nullable=False)   # Changed from Enum for SQLite
    voice = db.Column(db.String(50), nullable=False)  # Changed from Enum for SQLite
    person = db.Column(db.String(10), nullable=True)  # Changed from Enum for SQLite
    number = db.Column(db.String(20), nullable=True)  # Changed from Enum for SQLite
    form = db.Column(db.String(100), nullable=False)
    audio_url = db.Column(db.String(500))
    stress_pattern = db.Column(db.String(50))
    morphology = db.Column(db.Text)  # Changed from JSON for SQLite

    def to_dict(self):
        return {
            'id': self.id,
            'verb_id': self.verb_id,
            'tense': self.tense,
            'mood': self.mood,
            'voice': self.voice,
            'person': self.person,
            'number': self.number,
            'form': self.form,
            'audio_url': self.audio_url,
            'stress_pattern': self.stress_pattern,
            'morphology': self.morphology
        }

class UserProgress(db.Model):
    __tablename__ = 'user_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    verb_id = db.Column(db.Integer, db.ForeignKey('verbs.id'), nullable=False)
    conjugation_id = db.Column(db.Integer, db.ForeignKey('conjugations.id'), nullable=False)
    attempts = db.Column(db.Integer, default=0)
    correct_attempts = db.Column(db.Integer, default=0)
    last_attempt = db.Column(db.DateTime, nullable=True)
    next_review = db.Column(db.DateTime, nullable=True)
    ease_factor = db.Column(db.Float, default=2.50)  # Changed from Numeric for SQLite
    interval_days = db.Column(db.Integer, default=1)
    streak = db.Column(db.Integer, default=0)
    common_mistakes = db.Column(db.Text)  # Changed from JSON for SQLite
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'verb_id': self.verb_id,
            'conjugation_id': self.conjugation_id,
            'attempts': self.attempts,
            'correct_attempts': self.correct_attempts,
            'last_attempt': self.last_attempt.isoformat() if self.last_attempt else None,
            'next_review': self.next_review.isoformat() if self.next_review else None,
            'ease_factor': float(self.ease_factor),
            'interval_days': self.interval_days,
            'streak': self.streak,
            'common_mistakes': self.common_mistakes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PracticeSession(db.Model):
    __tablename__ = 'practice_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_type = db.Column(db.String(50), nullable=False)  # Changed from Enum for SQLite
    duration_seconds = db.Column(db.Integer)
    questions_attempted = db.Column(db.Integer)
    correct_answers = db.Column(db.Integer)
    verbs_practiced = db.Column(db.Text)  # Changed from JSON for SQLite
    accuracy_rate = db.Column(db.Float)    # Changed from Numeric for SQLite
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_type': self.session_type,
            'duration_seconds': self.duration_seconds,
            'questions_attempted': self.questions_attempted,
            'correct_answers': self.correct_answers,
            'verbs_practiced': self.verbs_practiced,
            'accuracy_rate': float(self.accuracy_rate) if self.accuracy_rate else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }