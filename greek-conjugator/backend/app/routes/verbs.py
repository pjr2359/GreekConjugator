from flask import Blueprint, jsonify, request, session
from ..models import db, Verb, Conjugation, UserProgress, PracticeSession
from .auth import login_required
from ..services.greek_text import GreekTextProcessor, compare_greek_texts
from datetime import datetime, timedelta
import random

bp = Blueprint('verbs', __name__, url_prefix='/api/verbs')

@bp.route('/', methods=['GET'])
@login_required
def get_verbs():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        difficulty = request.args.get('difficulty', type=int)
        verb_group = request.args.get('verb_group')
        
        query = Verb.query
        
        # Apply filters
        if difficulty:
            query = query.filter(Verb.difficulty == difficulty)
        if verb_group:
            query = query.filter(Verb.verb_group == verb_group)
            
        # Order by frequency for consistent results
        query = query.order_by(Verb.frequency)
        
        verbs = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'verbs': [verb.to_dict() for verb in verbs.items],
            'total_pages': verbs.pages,
            'current_page': verbs.page,
            'total_items': verbs.total
        })
    except Exception as e:
        return jsonify({'error': 'Failed to fetch verbs'}), 500

@bp.route('/<int:verb_id>', methods=['GET'])
@login_required
def get_verb(verb_id):
    try:
        verb = Verb.query.get_or_404(verb_id)
        return jsonify(verb.to_dict())
    except Exception as e:
        return jsonify({'error': 'Verb not found'}), 404

@bp.route('/<int:verb_id>/conjugations', methods=['GET'])
@login_required
def get_conjugations(verb_id):
    try:
        conjugations = Conjugation.query.filter_by(verb_id=verb_id).all()
        return jsonify([conjugation.to_dict() for conjugation in conjugations])
    except Exception as e:
        return jsonify({'error': 'Failed to fetch conjugations'}), 500

@bp.route('/practice/session', methods=['POST'])
@login_required
def start_practice_session():
    try:
        data = request.get_json()
        session_type = data.get('session_type', 'graded')
        difficulty_level = data.get('difficulty', 1)
        verb_count = data.get('verb_count', 10)
        
        user_id = session['user_id']
        
        # Get verbs based on user's subscription tier
        user_tier = session.get('subscription_tier', 'free')
        if user_tier == 'free':
            # Limit to first 50 verbs for free users
            verbs = Verb.query.filter(Verb.frequency <= 50).order_by(Verb.frequency).limit(verb_count).all()
        else:
            # Premium users get access to all verbs
            verbs = Verb.query.filter(Verb.difficulty <= difficulty_level).order_by(Verb.frequency).limit(verb_count).all()
        
        if not verbs:
            return jsonify({'error': 'No verbs found for practice'}), 404
            
        # Create practice session record
        practice_session = PracticeSession(
            user_id=user_id,
            session_type=session_type,
            questions_attempted=0,
            correct_answers=0,
            verbs_practiced=','.join(str(verb.id) for verb in verbs)  # Convert list to string for SQLite
        )
        db.session.add(practice_session)
        db.session.commit()
        
        return jsonify({
            'session_id': practice_session.id,
            'verbs': [verb.to_dict() for verb in verbs],
            'session_type': session_type
        })
    except Exception as e:
        return jsonify({'error': 'Failed to start practice session'}), 500

@bp.route('/practice/answer', methods=['POST'])
@login_required
def submit_answer():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        conjugation_id = data.get('conjugation_id')
        user_answer = data.get('answer', '').strip()
        is_correct = data.get('is_correct', False)
        
        user_id = session['user_id']
        
        # Get the conjugation
        conjugation = Conjugation.query.get_or_404(conjugation_id)
        
        # Enhanced answer validation using Greek text processing
        if user_answer and conjugation.form:
            # Use the enhanced Greek text processor for validation
            server_validation = compare_greek_texts(user_answer, conjugation.form)
            
            # If server validation differs from client validation, log for debugging
            if server_validation != is_correct:
                print(f"Validation mismatch: client={is_correct}, server={server_validation}")
                print(f"User answer: '{user_answer}', Correct: '{conjugation.form}'")
            
            # Use server validation as the authoritative answer
            is_correct = server_validation
        
        # Update or create user progress
        progress = UserProgress.query.filter_by(
            user_id=user_id,
            conjugation_id=conjugation_id
        ).first()
        
        if not progress:
            progress = UserProgress(
                user_id=user_id,
                verb_id=conjugation.verb_id,
                conjugation_id=conjugation_id
            )
            db.session.add(progress)
        
        # Update progress statistics
        progress.attempts += 1
        progress.last_attempt = datetime.utcnow()
        
        if is_correct:
            progress.correct_attempts += 1
            progress.streak += 1
            # Implement spaced repetition algorithm
            progress = update_spaced_repetition(progress, quality=4)  # Good answer
        else:
            progress.streak = 0
            progress = update_spaced_repetition(progress, quality=0)  # Wrong answer
            # Track common mistakes
            if progress.common_mistakes:
                mistakes_list = progress.common_mistakes.split(',') if progress.common_mistakes else []
                mistakes_list.append(user_answer)
                progress.common_mistakes = ','.join(mistakes_list)
            else:
                progress.common_mistakes = user_answer
        
        # Update practice session
        practice_session = PracticeSession.query.get(session_id)
        if practice_session:
            practice_session.questions_attempted += 1
            if is_correct:
                practice_session.correct_answers += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'correct': is_correct,
            'streak': progress.streak,
            'next_review': progress.next_review.isoformat() if progress.next_review else None
        })
    except Exception as e:
        return jsonify({'error': 'Failed to submit answer'}), 500

@bp.route('/practice/review', methods=['GET'])
@login_required
def get_review_cards():
    try:
        user_id = session['user_id']
        now = datetime.utcnow()
        
        # Get cards due for review
        due_cards = UserProgress.query.filter(
            UserProgress.user_id == user_id,
            UserProgress.next_review <= now
        ).limit(20).all()
        
        review_data = []
        for progress in due_cards:
            conjugation = Conjugation.query.get(progress.conjugation_id)
            verb = Verb.query.get(progress.verb_id)
            
            review_data.append({
                'progress_id': progress.id,
                'verb': verb.to_dict(),
                'conjugation': conjugation.to_dict(),
                'attempts': progress.attempts,
                'correct_attempts': progress.correct_attempts,
                'streak': progress.streak
            })
        
        return jsonify({
            'review_cards': review_data,
            'total_due': len(due_cards)
        })
    except Exception as e:
        return jsonify({'error': 'Failed to fetch review cards'}), 500

def update_spaced_repetition(progress, quality):
    """
    Implements SM-2 spaced repetition algorithm
    quality: 0-5 (0=wrong, 3=good, 5=perfect)
    """
    if quality < 3:
        # Reset interval for wrong answers
        progress.interval_days = 1
        progress.next_review = datetime.utcnow() + timedelta(days=1)
    else:
        # Adjust ease factor
        if quality == 3:
            pass  # No change to ease factor
        elif quality == 4:
            progress.ease_factor = min(progress.ease_factor + 0.1, 3.0)
        elif quality == 5:
            progress.ease_factor = min(progress.ease_factor + 0.15, 3.0)
        
        # Calculate new interval
        if progress.attempts == 1:
            progress.interval_days = 1
        elif progress.attempts == 2:
            progress.interval_days = 6
        else:
            progress.interval_days = int(progress.interval_days * progress.ease_factor)
        
        progress.next_review = datetime.utcnow() + timedelta(days=progress.interval_days)
    
    return progress

@bp.route('/stats', methods=['GET'])
@login_required
def get_user_stats():
    try:
        user_id = session['user_id']
        
        # Get overall statistics
        total_progress = UserProgress.query.filter_by(user_id=user_id).count()
        total_attempts = db.session.query(db.func.sum(UserProgress.attempts)).filter_by(user_id=user_id).scalar() or 0
        total_correct = db.session.query(db.func.sum(UserProgress.correct_attempts)).filter_by(user_id=user_id).scalar() or 0
        
        accuracy_rate = (total_correct / total_attempts * 100) if total_attempts > 0 else 0
        
        # Get recent sessions
        recent_sessions = PracticeSession.query.filter_by(user_id=user_id).order_by(PracticeSession.created_at.desc()).limit(10).all()
        
        # Get due cards count
        now = datetime.utcnow()
        due_cards = UserProgress.query.filter(
            UserProgress.user_id == user_id,
            UserProgress.next_review <= now
        ).count()
        
        return jsonify({
            'total_verbs_practiced': total_progress,
            'total_attempts': total_attempts,
            'total_correct': total_correct,
            'accuracy_rate': round(accuracy_rate, 2),
            'due_cards': due_cards,
            'recent_sessions': [session.to_dict() for session in recent_sessions]
        })
    except Exception as e:
        return jsonify({'error': 'Failed to fetch statistics'}), 500