"""
Vocabulary Practice API Routes
==============================

Provides endpoints for vocabulary flashcard practice with spaced repetition.
"""

from flask import Blueprint, jsonify, request, session
from ..models import db
from .auth import login_required
from ..services.greek_text import compare_greek_texts
from datetime import datetime, timedelta
import random
import re

bp = Blueprint('vocabulary', __name__, url_prefix='/api/vocabulary')


# ============================================================================
# VOCABULARY MODELS (using raw SQL since models aren't in models/__init__.py yet)
# ============================================================================

def get_word_by_id(word_id):
    """Get a word by ID."""
    result = db.session.execute(
        db.text("SELECT * FROM common_words WHERE id = :id"),
        {"id": word_id}
    ).fetchone()
    if result:
        return dict(result._mapping)
    return None


def get_user_vocab_progress(user_id, word_id):
    """Get user progress for a specific word."""
    result = db.session.execute(
        db.text("""
            SELECT * FROM user_vocabulary_progress 
            WHERE user_id = :user_id AND word_id = :word_id
        """),
        {"user_id": user_id, "word_id": word_id}
    ).fetchone()
    if result:
        return dict(result._mapping)
    return None


def create_user_vocab_progress(user_id, word_id):
    """Create initial progress record for a word."""
    db.session.execute(
        db.text("""
            INSERT INTO user_vocabulary_progress 
            (user_id, word_id, attempts, correct_attempts, ease_factor, interval_days, mastery_level)
            VALUES (:user_id, :word_id, 0, 0, 2.5, 1, 0)
        """),
        {"user_id": user_id, "word_id": word_id}
    )
    db.session.commit()


def get_today_new_words_count(user_id):
    """Count how many new words the user has started learning today."""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    result = db.session.execute(
        db.text("""
            SELECT COUNT(*) FROM user_vocabulary_progress 
            WHERE user_id = :user_id 
              AND created_at >= :today_start
        """),
        {"user_id": user_id, "today_start": today_start}
    ).fetchone()
    
    return result[0] if result else 0


def get_due_words_count(user_id):
    """Count words due for review."""
    result = db.session.execute(
        db.text("""
            SELECT COUNT(*) FROM user_vocabulary_progress 
            WHERE user_id = :user_id 
              AND next_review <= :now
        """),
        {"user_id": user_id, "now": datetime.utcnow()}
    ).fetchone()
    
    return result[0] if result else 0


def get_user_vocab_level(user_id):
    """
    Calculate user's vocabulary level and how many words they've unlocked.
    
    Progression system:
    - Start with top 100 words
    - For every 20 words mastered (mastery_level >= 3), unlock 50 more words
    - Max unlock is all words
    """
    # Count words with mastery level >= 3 (considered "learned")
    result = db.session.execute(
        db.text("""
            SELECT COUNT(*) FROM user_vocabulary_progress 
            WHERE user_id = :user_id AND mastery_level >= 3
        """),
        {"user_id": user_id}
    ).fetchone()
    
    mastered_count = result[0] if result else 0
    
    # Calculate unlocked words
    # Base: 100 words
    # Every 20 mastered words = unlock 50 more
    base_unlock = 100
    bonus_unlock = (mastered_count // 20) * 50
    unlocked_words = base_unlock + bonus_unlock
    
    # Get total available words
    total_result = db.session.execute(
        db.text("SELECT COUNT(*) FROM common_words")
    ).fetchone()
    total_words = total_result[0] if total_result else 0
    
    # Cap at total available
    unlocked_words = min(unlocked_words, total_words)
    
    # Calculate level (1-10 based on progress)
    level = min(1 + (mastered_count // 50), 10)
    
    # Words needed to unlock next batch
    words_to_next_unlock = 20 - (mastered_count % 20) if unlocked_words < total_words else 0
    
    return {
        'level': level,
        'mastered_count': mastered_count,
        'unlocked_words': unlocked_words,
        'total_words': total_words,
        'words_to_next_unlock': words_to_next_unlock,
        'next_unlock_amount': 50 if unlocked_words < total_words else 0
    }


def update_vocab_progress(user_id, word_id, is_correct):
    """Update user progress after an answer."""
    progress = get_user_vocab_progress(user_id, word_id)
    
    if not progress:
        create_user_vocab_progress(user_id, word_id)
        progress = get_user_vocab_progress(user_id, word_id)
    
    attempts = progress['attempts'] + 1
    correct_attempts = progress['correct_attempts'] + (1 if is_correct else 0)
    ease_factor = progress['ease_factor']
    interval_days = progress['interval_days']
    mastery_level = progress['mastery_level']
    
    # SM-2 algorithm
    if is_correct:
        # Increase ease factor for correct answers
        ease_factor = min(ease_factor + 0.1, 3.0)
        
        # Calculate new interval
        if attempts == 1:
            interval_days = 1
        elif attempts == 2:
            interval_days = 6
        else:
            interval_days = int(interval_days * ease_factor)
        
        # Increase mastery level
        mastery_level = min(mastery_level + 1, 5)
    else:
        # Reset for wrong answers
        ease_factor = max(ease_factor - 0.2, 1.3)
        interval_days = 1
        mastery_level = max(mastery_level - 1, 0)
    
    next_review = datetime.utcnow() + timedelta(days=interval_days)
    
    db.session.execute(
        db.text("""
            UPDATE user_vocabulary_progress 
            SET attempts = :attempts,
                correct_attempts = :correct_attempts,
                last_attempt = :last_attempt,
                next_review = :next_review,
                ease_factor = :ease_factor,
                interval_days = :interval_days,
                mastery_level = :mastery_level
            WHERE user_id = :user_id AND word_id = :word_id
        """),
        {
            "user_id": user_id,
            "word_id": word_id,
            "attempts": attempts,
            "correct_attempts": correct_attempts,
            "last_attempt": datetime.utcnow(),
            "next_review": next_review,
            "ease_factor": ease_factor,
            "interval_days": interval_days,
            "mastery_level": mastery_level
        }
    )
    db.session.commit()
    
    return {
        "attempts": attempts,
        "correct_attempts": correct_attempts,
        "mastery_level": mastery_level,
        "next_review": next_review.isoformat()
    }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@bp.route('/words', methods=['GET'])
@login_required
def get_words():
    """Get vocabulary words with optional filters."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        word_type = request.args.get('word_type')
        difficulty = request.args.get('difficulty', type=int)
        tags = request.args.get('tags')
        
        # Build query
        query = "SELECT * FROM common_words WHERE 1=1"
        params = {}
        
        if word_type:
            query += " AND word_type = :word_type"
            params['word_type'] = word_type
        
        if difficulty:
            query += " AND difficulty_level <= :difficulty"
            params['difficulty'] = difficulty
        
        if tags:
            query += " AND tags LIKE :tags"
            params['tags'] = f"%{tags}%"
        
        # Add pagination
        query += " ORDER BY frequency_rank LIMIT :limit OFFSET :offset"
        params['limit'] = per_page
        params['offset'] = (page - 1) * per_page
        
        result = db.session.execute(db.text(query), params).fetchall()
        words = [dict(row._mapping) for row in result]
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM common_words WHERE 1=1"
        if word_type:
            count_query += " AND word_type = :word_type"
        if difficulty:
            count_query += " AND difficulty_level <= :difficulty"
        if tags:
            count_query += " AND tags LIKE :tags"
        
        total = db.session.execute(db.text(count_query), params).fetchone()[0]
        
        return jsonify({
            'words': words,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })
    except Exception as e:
        print(f"Error fetching words: {e}")
        return jsonify({'error': 'Failed to fetch words'}), 500


@bp.route('/stats', methods=['GET'])
@login_required
def get_vocab_stats():
    """Get vocabulary statistics for the current user."""
    try:
        user_id = session['user_id']
        
        # Total words in database
        total_words = db.session.execute(
            db.text("SELECT COUNT(*) FROM common_words")
        ).fetchone()[0]
        
        # Words practiced by user
        words_practiced = db.session.execute(
            db.text("SELECT COUNT(*) FROM user_vocabulary_progress WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).fetchone()[0]
        
        # Total attempts and correct
        stats = db.session.execute(
            db.text("""
                SELECT 
                    COALESCE(SUM(attempts), 0) as total_attempts,
                    COALESCE(SUM(correct_attempts), 0) as total_correct
                FROM user_vocabulary_progress 
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        ).fetchone()
        
        total_attempts = stats[0] or 0
        total_correct = stats[1] or 0
        accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0
        
        # Words due for review
        due_count = db.session.execute(
            db.text("""
                SELECT COUNT(*) FROM user_vocabulary_progress 
                WHERE user_id = :user_id AND next_review <= :now
            """),
            {"user_id": user_id, "now": datetime.utcnow()}
        ).fetchone()[0]
        
        # Mastery breakdown
        mastery = db.session.execute(
            db.text("""
                SELECT mastery_level, COUNT(*) 
                FROM user_vocabulary_progress 
                WHERE user_id = :user_id
                GROUP BY mastery_level
            """),
            {"user_id": user_id}
        ).fetchall()
        
        mastery_breakdown = {row[0]: row[1] for row in mastery}
        
        # Word type breakdown
        word_types = db.session.execute(
            db.text("""
                SELECT word_type, COUNT(*) 
                FROM common_words 
                GROUP BY word_type 
                ORDER BY COUNT(*) DESC
            """)
        ).fetchall()
        
        # Get user's vocabulary level and unlocked words
        level_info = get_user_vocab_level(user_id)
        
        # Anki-style stats
        today_new_count = get_today_new_words_count(user_id)
        daily_new_limit = 10  # Default, could be user preference
        
        # Count new words available (not yet practiced)
        # For new users with 0 mastered words, ensure they always see at least the top 100 words
        unlocked_limit = max(level_info['unlocked_words'], 100) if level_info['mastered_count'] == 0 else level_info['unlocked_words']
        
        new_available = db.session.execute(
            db.text("""
                SELECT COUNT(*) FROM common_words 
                WHERE (frequency_rank <= :unlocked OR frequency_rank IS NULL)
                  AND id NOT IN (
                    SELECT word_id FROM user_vocabulary_progress WHERE user_id = :user_id
                  )
                LIMIT 100
            """),
            {"user_id": user_id, "unlocked": unlocked_limit}
        ).fetchone()[0]
        
        # Ensure new users always see at least 10 new words available
        if level_info['mastered_count'] == 0 and new_available < 10:
            # Count total words in database
            total_available = db.session.execute(
                db.text("SELECT COUNT(*) FROM common_words")
            ).fetchone()[0]
            new_available = min(total_available, 10)
        
        return jsonify({
            'total_words': total_words,
            'words_practiced': words_practiced,
            'total_attempts': total_attempts,
            'total_correct': total_correct,
            'accuracy_rate': round(accuracy, 1),
            'due_for_review': due_count,
            'mastery_breakdown': mastery_breakdown,
            'word_types': {row[0]: row[1] for row in word_types},
            # Level/progression fields
            'level': level_info['level'],
            'mastered_count': level_info['mastered_count'],
            'unlocked_words': level_info['unlocked_words'],
            'words_to_next_unlock': level_info['words_to_next_unlock'],
            'next_unlock_amount': level_info['next_unlock_amount'],
            # Anki-style fields
            'today_new_count': today_new_count,
            'daily_new_limit': daily_new_limit,
            'new_words_remaining': max(0, daily_new_limit - today_new_count),
            'new_available': new_available
        })
    except Exception as e:
        print(f"Error fetching vocab stats: {e}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500


@bp.route('/practice/smart', methods=['POST'])
@login_required
def smart_practice():
    """
    Anki-style smart practice session.
    Combines due reviews with new words up to daily limit.
    """
    try:
        data = request.get_json() or {}
        daily_new_limit = data.get('daily_new_limit', 10)  # Default 10 new words/day
        direction = data.get('direction', 'greek_to_english')
        
        user_id = session['user_id']
        
        # Get user's level and unlocked words
        level_info = get_user_vocab_level(user_id)
        unlocked_words = level_info['unlocked_words']
        
        # Get counts
        today_new_count = get_today_new_words_count(user_id)
        due_count = get_due_words_count(user_id)
        new_words_remaining = max(0, daily_new_limit - today_new_count)
        
        words = []
        
        # 1. First, get all due reviews (priority)
        if due_count > 0:
            due_query = """
                SELECT cw.*, 'review' as card_type FROM common_words cw
                JOIN user_vocabulary_progress uvp ON cw.id = uvp.word_id
                WHERE uvp.user_id = :user_id 
                  AND uvp.next_review <= :now
                ORDER BY uvp.next_review ASC
                LIMIT 50
            """
            due_result = db.session.execute(
                db.text(due_query),
                {"user_id": user_id, "now": datetime.utcnow()}
            ).fetchall()
            words.extend([dict(row._mapping) for row in due_result])
        
        # 2. Then, add new words if we haven't hit daily limit
        if new_words_remaining > 0:
            # For new users, ensure they can access words even if frequency_rank is NULL
            # Use a minimum unlocked count of 100 for brand new users
            effective_unlocked = max(unlocked_words, 100) if get_user_vocab_level(user_id)['mastered_count'] == 0 else unlocked_words
            
            new_query = """
                SELECT *, 'new' as card_type FROM common_words 
                WHERE (frequency_rank <= :unlocked OR frequency_rank IS NULL)
                  AND id NOT IN (
                    SELECT word_id FROM user_vocabulary_progress WHERE user_id = :user_id
                  )
                ORDER BY COALESCE(frequency_rank, 999999) ASC
                LIMIT :limit
            """
            new_result = db.session.execute(
                db.text(new_query),
                {"user_id": user_id, "unlocked": effective_unlocked, "limit": new_words_remaining}
            ).fetchall()
            words.extend([dict(row._mapping) for row in new_result])
        
        if not words:
            return jsonify({
                'error': 'all_done',
                'message': 'No cards to review! You\'ve completed all due reviews and reached your daily new word limit.',
                'due_count': 0,
                'new_remaining': 0,
                'today_new_count': today_new_count,
                'daily_new_limit': daily_new_limit
            }), 200  # Return 200 with special status
        
        # Shuffle to mix reviews and new words
        import random
        random.shuffle(words)
        
        return jsonify({
            'words': words,
            'count': len(words),
            'direction': direction,
            'practice_type': 'smart',
            'due_count': due_count,
            'new_count': len([w for w in words if w.get('card_type') == 'new']),
            'review_count': len([w for w in words if w.get('card_type') == 'review']),
            'today_new_count': today_new_count,
            'new_words_remaining': new_words_remaining,
            'daily_new_limit': daily_new_limit,
            'level_info': level_info
        })
    except Exception as e:
        print(f"Error in smart practice: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to start smart practice'}), 500


@bp.route('/practice/start', methods=['POST'])
@login_required
def start_practice():
    """Start a vocabulary practice session (manual mode selection)."""
    try:
        data = request.get_json() or {}
        practice_type = data.get('type', 'random')  # 'random', 'review', 'new', 'category'
        word_type = data.get('word_type')  # 'noun', 'adjective', etc.
        category = data.get('category')  # 'food', 'travel', etc.
        count = data.get('count', 10)
        direction = data.get('direction', 'greek_to_english')  # or 'english_to_greek'
        
        user_id = session['user_id']
        
        # Get user's unlocked word count (progressive difficulty)
        level_info = get_user_vocab_level(user_id)
        unlocked_words = level_info['unlocked_words']
        
        # Build query based on practice type
        if practice_type == 'review':
            # Get words due for review (from unlocked words only)
            query = """
                SELECT cw.* FROM common_words cw
                JOIN user_vocabulary_progress uvp ON cw.id = uvp.word_id
                WHERE uvp.user_id = :user_id 
                  AND uvp.next_review <= :now
                  AND cw.frequency_rank <= :unlocked
            """
            params = {"user_id": user_id, "now": datetime.utcnow(), "unlocked": unlocked_words}
        elif practice_type == 'new':
            # Get new words not yet practiced (from unlocked words only)
            query = """
                SELECT * FROM common_words 
                WHERE frequency_rank <= :unlocked
                  AND id NOT IN (
                    SELECT word_id FROM user_vocabulary_progress WHERE user_id = :user_id
                  )
            """
            params = {"user_id": user_id, "unlocked": unlocked_words}
        else:
            # Random words from unlocked pool
            query = "SELECT * FROM common_words WHERE frequency_rank <= :unlocked"
            params = {"unlocked": unlocked_words}
        
        # Apply filters
        if word_type:
            query += " AND word_type = :word_type"
            params['word_type'] = word_type
        
        if category:
            query += " AND tags LIKE :category"
            params['category'] = f"%{category}%"
        
        # Random selection, prioritizing words not yet mastered
        query += " ORDER BY RANDOM() LIMIT :count"
        params['count'] = count
        
        result = db.session.execute(db.text(query), params).fetchall()
        words = [dict(row._mapping) for row in result]
        
        if not words:
            return jsonify({'error': 'No words found matching criteria. Try practicing your current words to unlock more!'}), 404
        
        return jsonify({
            'words': words,
            'count': len(words),
            'direction': direction,
            'practice_type': practice_type,
            'level_info': level_info  # Include level info in response
        })
    except Exception as e:
        print(f"Error starting practice: {e}")
        return jsonify({'error': 'Failed to start practice'}), 500


@bp.route('/practice/question', methods=['POST'])
@login_required
def get_question():
    """Get a single practice question with multiple choice options."""
    try:
        data = request.get_json() or {}
        word_id = data.get('word_id')
        direction = data.get('direction', 'greek_to_english')
        question_type = data.get('question_type', 'multiple_choice')  # 'multiple_choice' or 'type'
        
        if not word_id:
            return jsonify({'error': 'word_id required'}), 400
        
        word = get_word_by_id(word_id)
        if not word:
            return jsonify({'error': 'Word not found'}), 404
        
        # Generate question
        if direction == 'greek_to_english':
            question_text = word['word']
            correct_answer = word['english'].split(';')[0].strip()  # First meaning
        else:
            question_text = word['english'].split(';')[0].strip()
            correct_answer = word['word']
        
        response = {
            'word_id': word_id,
            'question': question_text,
            'correct_answer': correct_answer,
            'direction': direction,
            'word_type': word['word_type'],
            'full_translation': word['english']
        }
        
        # Generate multiple choice options if requested
        if question_type == 'multiple_choice':
            def _normalize_option(text):
                if not text:
                    return ""
                normalized = text.lower().strip()
                normalized = re.sub(r'[^\w\s]', '', normalized)
                normalized = re.sub(r'\s+', ' ', normalized)
                return normalized

            def _is_distinct(candidate, existing_norms):
                candidate_norm = _normalize_option(candidate)
                if not candidate_norm:
                    return False
                if candidate_norm in existing_norms:
                    return False
                for norm in existing_norms:
                    if candidate_norm in norm or norm in candidate_norm:
                        return False
                return True

            # Get similar words for wrong answers - prioritize common words with clean translations
            if direction == 'greek_to_english':
                # Get other English translations as wrong answers
                # Filter for quality: common words, reasonable length translations
                wrong_query = """
                    SELECT english FROM common_words 
                    WHERE id != :word_id 
                      AND word_type = :word_type
                      AND frequency_rank < 5000
                      AND length(english) > 2
                      AND length(english) < 60
                      AND english NOT LIKE '%singular of%'
                      AND english NOT LIKE '%plural of%'
                      AND english NOT LIKE '%person %'
                      AND english NOT LIKE '%tense%'
                      AND english NOT LIKE '%;%'
                      AND english NOT LIKE '%misspelling%'
                      AND english NOT LIKE '%contraction%'
                      AND english NOT LIKE '%alternative%'
                      AND english NOT LIKE '%spelling of%'
                      AND english NOT LIKE '%form of%'
                    ORDER BY frequency_rank, RANDOM() 
                    LIMIT 10
                """
            else:
                # Get other Greek words as wrong answers
                wrong_query = """
                    SELECT word FROM common_words 
                    WHERE id != :word_id 
                      AND word_type = :word_type
                      AND frequency_rank < 5000
                    ORDER BY frequency_rank, RANDOM() 
                    LIMIT 10
                """
            
            def _collect_wrong_answers(query, params, existing_norms, answers, limit=3):
                results = db.session.execute(db.text(query), params).fetchall()
                for row in results:
                    answer = row[0].split(';')[0].strip()
                    if (answer.lower() != correct_answer.lower()
                        and len(answer) > 1
                        and len(answer) < 60
                        and 'of ' not in answer.lower()[:10]  # Skip "plural of", etc.
                        and _is_distinct(answer, existing_norms)
                        and answer not in answers):
                        answers.append(answer)
                        existing_norms.add(_normalize_option(answer))
                    if len(answers) >= limit:
                        break

            # Clean up wrong answers - take first meaning only, filter bad ones
            wrong_answers = []
            wrong_answer_norms = {_normalize_option(correct_answer)}
            _collect_wrong_answers(
                wrong_query,
                {"word_id": word_id, "word_type": word['word_type']},
                wrong_answer_norms,
                wrong_answers
            )

            # Fallback: broaden search if we don't have enough distinct options
            if len(wrong_answers) < 3:
                if direction == 'greek_to_english':
                    fallback_query = """
                        SELECT english FROM common_words
                        WHERE id != :word_id
                          AND length(english) > 2
                          AND length(english) < 80
                          AND english NOT LIKE '%singular of%'
                          AND english NOT LIKE '%plural of%'
                          AND english NOT LIKE '%person %'
                          AND english NOT LIKE '%tense%'
                          AND english NOT LIKE '%;%'
                          AND english NOT LIKE '%misspelling%'
                          AND english NOT LIKE '%contraction%'
                          AND english NOT LIKE '%alternative%'
                          AND english NOT LIKE '%spelling of%'
                          AND english NOT LIKE '%form of%'
                        ORDER BY RANDOM()
                        LIMIT 200
                    """
                else:
                    fallback_query = """
                        SELECT word FROM common_words
                        WHERE id != :word_id
                        ORDER BY RANDOM()
                        LIMIT 200
                    """

                _collect_wrong_answers(
                    fallback_query,
                    {"word_id": word_id},
                    wrong_answer_norms,
                    wrong_answers
                )

            if len(wrong_answers) < 3:
                return jsonify({'error': 'Insufficient distinct options for multiple choice'}), 500
            
            # Combine and shuffle options
            options = [correct_answer] + wrong_answers[:3]
            random.shuffle(options)
            
            response['options'] = options
            response['question_type'] = 'multiple_choice'
        else:
            response['question_type'] = 'type'
        
        return jsonify(response)
    except Exception as e:
        print(f"Error generating question: {e}")
        return jsonify({'error': 'Failed to generate question'}), 500


@bp.route('/practice/answer', methods=['POST'])
@login_required
def submit_answer():
    """Submit an answer and update progress."""
    try:
        data = request.get_json()
        word_id = data.get('word_id')
        user_answer = data.get('answer', '').strip()
        correct_answer = data.get('correct_answer', '').strip()
        direction = data.get('direction', 'greek_to_english')
        
        if not word_id:
            return jsonify({'error': 'word_id required'}), 400
        
        user_id = session['user_id']
        
        # Check if answer is correct
        if direction == 'greek_to_english':
            # More lenient matching for English
            is_correct = user_answer.lower() == correct_answer.lower()
        else:
            # Use Greek text comparison for Greek answers
            is_correct = compare_greek_texts(user_answer, correct_answer)
        
        # Update progress
        progress = update_vocab_progress(user_id, word_id, is_correct)
        
        return jsonify({
            'correct': is_correct,
            'correct_answer': correct_answer,
            'progress': progress
        })
    except Exception as e:
        print(f"Error submitting answer: {e}")
        return jsonify({'error': 'Failed to submit answer'}), 500


@bp.route('/categories', methods=['GET'])
@login_required
def get_categories():
    """Get available vocabulary categories/tags."""
    try:
        # Get all unique tags
        result = db.session.execute(
            db.text("SELECT DISTINCT tags FROM common_words WHERE tags != '' AND tags IS NOT NULL")
        ).fetchall()
        
        # Parse and count tags
        tag_counts = {}
        for row in result:
            tags = row[0].split(',') if row[0] else []
            for tag in tags:
                tag = tag.strip()
                if tag:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Also get word type counts
        word_types = db.session.execute(
            db.text("SELECT word_type, COUNT(*) FROM common_words GROUP BY word_type ORDER BY COUNT(*) DESC")
        ).fetchall()
        
        return jsonify({
            'categories': tag_counts,
            'word_types': {row[0]: row[1] for row in word_types}
        })
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return jsonify({'error': 'Failed to fetch categories'}), 500


@bp.route('/word/<int:word_id>', methods=['GET'])
@login_required
def get_word(word_id):
    """Get details for a specific word."""
    try:
        word = get_word_by_id(word_id)
        if not word:
            return jsonify({'error': 'Word not found'}), 404
        
        # Get user progress if any
        user_id = session['user_id']
        progress = get_user_vocab_progress(user_id, word_id)
        
        return jsonify({
            'word': word,
            'progress': progress
        })
    except Exception as e:
        print(f"Error fetching word: {e}")
        return jsonify({'error': 'Failed to fetch word'}), 500

