"""
Conjugation Skills & Progress API Routes
Handles skill tree, progress tracking, and mastery levels
"""

from flask import Blueprint, jsonify, request, session
from ..models import db
from datetime import datetime
from functools import wraps

bp = Blueprint('skills', __name__, url_prefix='/api/skills')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def get_user_skills(user_id):
    """Get all skill progress for a user, initializing if needed."""
    # Get all skill definitions
    definitions = db.session.execute(
        db.text("SELECT * FROM conjugation_skill_definitions ORDER BY tier, difficulty")
    ).fetchall()
    
    # Get user's current skill progress
    user_skills = db.session.execute(
        db.text("SELECT * FROM user_conjugation_skills WHERE user_id = :user_id"),
        {"user_id": user_id}
    ).fetchall()
    
    user_skills_map = {s[2]: s for s in user_skills}  # category -> skill row
    
    skills = []
    for defn in definitions:
        category = defn[1]
        user_skill = user_skills_map.get(category)
        
        # Check if skill should be unlocked
        unlock_req = defn[8]  # unlock_requirement column
        is_unlocked = False
        
        if unlock_req is None:
            # First skill - always unlocked
            is_unlocked = True
        elif unlock_req in user_skills_map:
            # Check if prerequisite is mastered (level >= 3)
            prereq = user_skills_map[unlock_req]
            if prereq[6] >= 3:  # mastery_level column
                is_unlocked = True
        
        # Initialize skill if not exists
        if not user_skill:
            db.session.execute(
                db.text("""
                    INSERT OR IGNORE INTO user_conjugation_skills 
                    (user_id, category, tier, unlocked, mastery_level)
                    VALUES (:user_id, :category, :tier, :unlocked, :mastery)
                """),
                {
                    "user_id": user_id,
                    "category": category,
                    "tier": defn[4],
                    "unlocked": is_unlocked,
                    "mastery": 1 if is_unlocked else 0
                }
            )
            db.session.commit()
            
            # Refetch
            user_skill = db.session.execute(
                db.text("SELECT * FROM user_conjugation_skills WHERE user_id = :user_id AND category = :category"),
                {"user_id": user_id, "category": category}
            ).fetchone()
        
        skills.append({
            'category': category,
            'display_name': defn[2],
            'display_name_greek': defn[3],
            'tier': defn[4],
            'difficulty': defn[5],
            'icon': defn[6],
            'description': defn[7],
            'unlock_requirement': defn[8],
            'form_count': defn[9],
            'attempts': user_skill[4] if user_skill else 0,
            'correct': user_skill[5] if user_skill else 0,
            'mastery_level': user_skill[6] if user_skill else 0,
            'unlocked': user_skill[7] if user_skill else is_unlocked,
            'accuracy': round((user_skill[5] / user_skill[4]) * 100, 1) if user_skill and user_skill[4] > 0 else 0
        })
    
    return skills


def calculate_mastery_level(attempts, correct):
    """Calculate mastery level based on attempts and accuracy."""
    if attempts < 5:
        return 1  # Need minimum attempts
    
    accuracy = correct / attempts
    
    if accuracy >= 0.95 and attempts >= 50:
        return 5  # Master
    elif accuracy >= 0.85 and attempts >= 30:
        return 4  # Expert
    elif accuracy >= 0.75 and attempts >= 20:
        return 3  # Proficient (unlocks next skill)
    elif accuracy >= 0.60 and attempts >= 10:
        return 2  # Developing
    else:
        return 1  # Beginner


@bp.route('/tree', methods=['GET'])
@login_required
def get_skill_tree():
    """Get the complete skill tree with user progress."""
    try:
        user_id = session['user_id']
        skills = get_user_skills(user_id)
        
        # Organize by tier
        tiers = {}
        for skill in skills:
            tier = skill['tier']
            if tier not in tiers:
                tiers[tier] = []
            tiers[tier].append(skill)
        
        # Calculate overall stats
        total_mastery = sum(s['mastery_level'] for s in skills)
        max_mastery = len(skills) * 5
        unlocked_count = sum(1 for s in skills if s['unlocked'])
        
        return jsonify({
            'skills': skills,
            'tiers': tiers,
            'total_skills': len(skills),
            'unlocked_skills': unlocked_count,
            'overall_mastery': total_mastery,
            'max_mastery': max_mastery,
            'mastery_percentage': round((total_mastery / max_mastery) * 100, 1) if max_mastery > 0 else 0
        })
    except Exception as e:
        print(f"Error fetching skill tree: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch skill tree'}), 500


@bp.route('/category/<category>', methods=['GET'])
@login_required
def get_skill_detail(category):
    """Get detailed info for a specific skill category."""
    try:
        user_id = session['user_id']
        
        # Get skill definition
        defn = db.session.execute(
            db.text("SELECT * FROM conjugation_skill_definitions WHERE category = :cat"),
            {"cat": category}
        ).fetchone()
        
        if not defn:
            return jsonify({'error': 'Skill not found'}), 404
        
        # Get user progress
        user_skill = db.session.execute(
            db.text("SELECT * FROM user_conjugation_skills WHERE user_id = :uid AND category = :cat"),
            {"uid": user_id, "cat": category}
        ).fetchone()
        
        # Parse category to get tense, mood, voice
        parts = category.split('_')
        tense = parts[0]
        mood = parts[1]
        voice = parts[2] if len(parts) > 2 else 'active'
        
        # Get sample conjugations for this category
        samples = db.session.execute(
            db.text("""
                SELECT c.form, v.infinitive, v.english 
                FROM conjugations c
                JOIN verbs v ON c.verb_id = v.id
                WHERE c.tense = :tense AND c.mood = :mood AND c.voice = :voice
                ORDER BY RANDOM()
                LIMIT 5
            """),
            {"tense": tense, "mood": mood, "voice": voice}
        ).fetchall()
        
        return jsonify({
            'category': category,
            'display_name': defn[2],
            'display_name_greek': defn[3],
            'tier': defn[4],
            'difficulty': defn[5],
            'icon': defn[6],
            'description': defn[7],
            'form_count': defn[9],
            'attempts': user_skill[4] if user_skill else 0,
            'correct': user_skill[5] if user_skill else 0,
            'mastery_level': user_skill[6] if user_skill else 0,
            'unlocked': user_skill[7] if user_skill else False,
            'samples': [{'form': s[0], 'verb': s[1], 'english': s[2]} for s in samples],
            'mastery_requirements': {
                1: {'name': 'Beginner', 'min_attempts': 0, 'min_accuracy': 0},
                2: {'name': 'Developing', 'min_attempts': 10, 'min_accuracy': 60},
                3: {'name': 'Proficient', 'min_attempts': 20, 'min_accuracy': 75},
                4: {'name': 'Expert', 'min_attempts': 30, 'min_accuracy': 85},
                5: {'name': 'Master', 'min_attempts': 50, 'min_accuracy': 95},
            }
        })
    except Exception as e:
        print(f"Error fetching skill detail: {e}")
        return jsonify({'error': 'Failed to fetch skill detail'}), 500


@bp.route('/record', methods=['POST'])
@login_required
def record_practice():
    """Record practice result for a skill category."""
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        category = data.get('category')
        is_correct = data.get('correct', False)
        
        if not category:
            return jsonify({'error': 'Category required'}), 400
        
        # Update user skill progress
        db.session.execute(
            db.text("""
                UPDATE user_conjugation_skills 
                SET attempts = attempts + 1,
                    correct = correct + :correct,
                    last_practice = :now
                WHERE user_id = :user_id AND category = :category
            """),
            {
                "user_id": user_id,
                "category": category,
                "correct": 1 if is_correct else 0,
                "now": datetime.utcnow()
            }
        )
        db.session.commit()
        
        # Get updated stats
        user_skill = db.session.execute(
            db.text("SELECT * FROM user_conjugation_skills WHERE user_id = :uid AND category = :cat"),
            {"uid": user_id, "cat": category}
        ).fetchone()
        
        # Calculate new mastery level
        new_mastery = calculate_mastery_level(user_skill[4], user_skill[5])
        old_mastery = user_skill[6]
        
        # Update mastery level if changed
        if new_mastery != old_mastery:
            db.session.execute(
                db.text("UPDATE user_conjugation_skills SET mastery_level = :level WHERE user_id = :uid AND category = :cat"),
                {"level": new_mastery, "uid": user_id, "cat": category}
            )
            db.session.commit()
            
            # Check if we should unlock new skills
            if new_mastery >= 3:
                # Find skills that require this category and unlock them
                db.session.execute(
                    db.text("""
                        UPDATE user_conjugation_skills 
                        SET unlocked = TRUE, mastery_level = CASE WHEN mastery_level = 0 THEN 1 ELSE mastery_level END
                        WHERE user_id = :uid 
                          AND category IN (
                              SELECT category FROM conjugation_skill_definitions 
                              WHERE unlock_requirement = :cat
                          )
                    """),
                    {"uid": user_id, "cat": category}
                )
                db.session.commit()
        
        return jsonify({
            'success': True,
            'attempts': user_skill[4],
            'correct': user_skill[5],
            'accuracy': round((user_skill[5] / user_skill[4]) * 100, 1) if user_skill[4] > 0 else 0,
            'mastery_level': new_mastery,
            'level_up': new_mastery > old_mastery,
            'unlocked_new': new_mastery >= 3 and old_mastery < 3
        })
    except Exception as e:
        print(f"Error recording practice: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to record practice'}), 500


@bp.route('/stats', methods=['GET'])
@login_required
def get_overall_stats():
    """Get overall conjugation learning statistics."""
    try:
        user_id = session['user_id']
        skills = get_user_skills(user_id)
        
        # Calculate stats per tier
        tier_stats = {}
        for skill in skills:
            tier = skill['tier']
            if tier not in tier_stats:
                tier_stats[tier] = {'total': 0, 'unlocked': 0, 'mastery_sum': 0, 'attempts': 0, 'correct': 0}
            tier_stats[tier]['total'] += 1
            tier_stats[tier]['unlocked'] += 1 if skill['unlocked'] else 0
            tier_stats[tier]['mastery_sum'] += skill['mastery_level']
            tier_stats[tier]['attempts'] += skill['attempts']
            tier_stats[tier]['correct'] += skill['correct']
        
        # Overall stats
        total_attempts = sum(s['attempts'] for s in skills)
        total_correct = sum(s['correct'] for s in skills)
        
        return jsonify({
            'total_skills': len(skills),
            'unlocked_skills': sum(1 for s in skills if s['unlocked']),
            'mastered_skills': sum(1 for s in skills if s['mastery_level'] >= 5),
            'proficient_skills': sum(1 for s in skills if s['mastery_level'] >= 3),
            'total_attempts': total_attempts,
            'total_correct': total_correct,
            'overall_accuracy': round((total_correct / total_attempts) * 100, 1) if total_attempts > 0 else 0,
            'tier_stats': tier_stats,
            'current_level': sum(1 for s in skills if s['mastery_level'] >= 3),  # Skills at proficient+
            'next_unlock': next((s for s in skills if not s['unlocked']), None)
        })
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return jsonify({'error': 'Failed to fetch stats'}), 500


@bp.route('/progress', methods=['GET'])
@login_required
def get_progress():
    """Get user's overall progress for gamification display."""
    try:
        user_id = session['user_id']
        skills = get_user_skills(user_id)
        
        # Calculate overall stats
        total_attempts = sum(s['attempts'] for s in skills)
        total_correct = sum(s['correct'] for s in skills)
        skills_mastered = sum(1 for s in skills if s['mastery_level'] >= 5)
        skills_proficient = sum(1 for s in skills if s['mastery_level'] >= 3)
        
        # Calculate streak (placeholder - would need practice history)
        # For now, estimate based on recent accuracy
        current_streak = 0
        
        return jsonify({
            'total_attempts': total_attempts,
            'total_correct': total_correct,
            'overall_accuracy': round((total_correct / total_attempts) * 100, 1) if total_attempts > 0 else 0,
            'skills_mastered': skills_mastered,
            'skills_proficient': skills_proficient,
            'total_skills': len(skills),
            'current_streak': current_streak,
            'level': skills_proficient + 1,  # Level based on proficient skills
            'xp_total': (total_correct * 10) + (total_attempts * 2),
            'xp_to_next_level': 100
        })
    except Exception as e:
        print(f"Error fetching progress: {e}")
        return jsonify({'error': 'Failed to fetch progress'}), 500

