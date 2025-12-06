from flask import Blueprint, jsonify, request, session
from ..models import db, Verb, Conjugation, UserProgress, PracticeSession
from .auth import login_required
from ..services.greek_text import GreekTextProcessor, compare_greek_texts
from ..services.skill import calculate_skill_level
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
        difficulty_level = data.get('difficulty', 3)  # Default to max difficulty to include all verbs
        verb_count = data.get('verb_count', 10)
        
        user_id = session['user_id']
        
        # All users get access to all verbs with reasonable difficulty filtering
        if difficulty_level < 3:
            difficulty_level = 3  # Ensure we get a reasonable number of verbs
        
        # Debug logging
        print(f"DEBUG: Starting practice session with difficulty={difficulty_level}, verb_count={verb_count}")
        
        # Get all verbs with conjugations for this difficulty level
        verbs_with_conjugations = Verb.query.join(Conjugation).filter(Verb.difficulty <= difficulty_level).distinct().all()
        print(f"DEBUG: Found {len(verbs_with_conjugations)} verbs with conjugations for difficulty <= {difficulty_level}")
        
        # Randomly select a subset for this session to provide variety
        if len(verbs_with_conjugations) >= verb_count:
            verbs = random.sample(verbs_with_conjugations, verb_count)
        else:
            verbs = verbs_with_conjugations
        random.shuffle(verbs)  # Shuffle the order for additional randomness
        print(f"DEBUG: Selected {len(verbs)} verbs for practice session")
        
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
        
        # Pre-load all conjugations for the selected verbs (eliminates N+1 API calls)
        verb_ids = [verb.id for verb in verbs]
        all_conjugations = Conjugation.query.filter(Conjugation.verb_id.in_(verb_ids)).all()
        
        # Group conjugations by verb_id
        conjugations_map = {}
        for conj in all_conjugations:
            if conj.verb_id not in conjugations_map:
                conjugations_map[conj.verb_id] = []
            conjugations_map[conj.verb_id].append(conj.to_dict())
        
        # Build verb data with conjugations included
        verbs_with_conjugations = []
        for verb in verbs:
            verb_data = verb.to_dict()
            verb_data['conjugations'] = conjugations_map.get(verb.id, [])
            verbs_with_conjugations.append(verb_data)
        
        return jsonify({
            'session_id': practice_session.id,
            'verbs': verbs_with_conjugations,
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
                conjugation_id=conjugation_id,
                attempts=0,
                correct_attempts=0,
                streak=0,
                ease_factor=2.50,
                interval_days=1
            )
            db.session.add(progress)
        
        # Update progress statistics
        progress.attempts = (progress.attempts or 0) + 1
        progress.last_attempt = datetime.utcnow()
        
        if is_correct:
            progress.correct_attempts = (progress.correct_attempts or 0) + 1
            progress.streak = (progress.streak or 0) + 1
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
            practice_session.questions_attempted = (practice_session.questions_attempted or 0) + 1
            if is_correct:
                practice_session.correct_answers = (practice_session.correct_answers or 0) + 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'correct': is_correct,
            'streak': progress.streak,
            'next_review': progress.next_review.isoformat() if progress.next_review else None
        })
    except Exception as e:
        print(f"Error in submit_answer: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to submit answer: {str(e)}'}), 500

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
        skill_level = calculate_skill_level(total_correct, accuracy_rate)
        
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
            'skill_level': skill_level,
            'due_cards': due_cards,
            'recent_sessions': [session.to_dict() for session in recent_sessions]
        })
    except Exception as e:
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@bp.route('/practice/question', methods=['POST'])
@login_required
def generate_practice_question():
    """Generate enhanced practice questions with translations and multiple choice options"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        verb_id = data.get('verb_id')
        question_type = data.get('question_type', 'conjugation')  # 'conjugation', 'multiple_choice'
        
        user_id = session['user_id']
        
        # Get the verb and its conjugations
        verb = Verb.query.get_or_404(verb_id)
        conjugations = Conjugation.query.filter_by(verb_id=verb_id).all()
        
        if not conjugations:
            return jsonify({'error': 'No conjugations found for this verb'}), 404
        
        # Select a random conjugation for the question
        target_conjugation = random.choice(conjugations)
        
        # Generate question based on type
        if question_type == 'multiple_choice':
            # Generate multiple choice options
            correct_answer = target_conjugation.form
            
            # Get wrong answers from other conjugations of the same verb and other verbs
            all_forms = [c.form for c in conjugations if c.form != correct_answer]
            
            # Add some forms from other verbs for more variety
            other_conjugations = Conjugation.query.filter(
                Conjugation.verb_id != verb_id,
                Conjugation.tense == target_conjugation.tense,
                Conjugation.mood == target_conjugation.mood,
                Conjugation.person == target_conjugation.person,
                Conjugation.number == target_conjugation.number
            ).limit(10).all()
            
            all_forms.extend([c.form for c in other_conjugations])
            
            # Select 3 random wrong answers
            wrong_answers = random.sample(all_forms, min(3, len(all_forms)))
            
            # Create options list and shuffle
            options = [correct_answer] + wrong_answers
            random.shuffle(options)
            
            question_data = {
                'type': 'multiple_choice',
                'verb': verb.to_dict(),
                'conjugation': target_conjugation.to_dict(),
                'question': f"How do you conjugate '{verb.infinitive}' ({verb.english}) in {target_conjugation.tense} tense, {target_conjugation.mood} mood, {target_conjugation.person} person {target_conjugation.number}?",
                'options': options,
                'correct_answer': correct_answer,
                'translation': verb.english
            }
        else:
            # Standard conjugation question
            question_data = {
                'type': 'conjugation',
                'verb': verb.to_dict(),
                'conjugation': target_conjugation.to_dict(),
                'question': f"Conjugate '{verb.infinitive}' ({verb.english}) in {target_conjugation.tense} tense, {target_conjugation.mood} mood, {target_conjugation.person} person {target_conjugation.number}",
                'correct_answer': target_conjugation.form,
                'translation': verb.english,
                'hint': f"The verb means '{verb.english}'"
            }
        
        return jsonify(question_data)
        
    except Exception as e:
        print(f"Error generating practice question: {str(e)}")
        return jsonify({'error': 'Failed to generate question'}), 500
