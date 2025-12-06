"""
Dashboard API - Comprehensive learning metrics and recommendations
"""

from flask import Blueprint, jsonify, session
from ..models import db
from .auth import login_required
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


# ============================================================================
# VOCABULARY TIERS - Based on real Greek language learning research
# ============================================================================
VOCABULARY_TIERS = [
    {"threshold": 0, "name": "Beginner", "greek": "Αρχάριος", "description": "Just starting out", "unlock": None},
    {"threshold": 100, "name": "Tourist", "greek": "Τουρίστας", "description": "Basic survival phrases", "unlock": "Café conversations"},
    {"threshold": 250, "name": "Explorer", "greek": "Εξερευνητής", "description": "Can handle simple interactions", "unlock": "Market dialogues"},
    {"threshold": 500, "name": "Conversant", "greek": "Συνομιλητής", "description": "Basic daily conversations", "unlock": "Story mode: A1"},
    {"threshold": 1000, "name": "Competent", "greek": "Ικανός", "description": "Comfortable in everyday situations", "unlock": "Listening exercises"},
    {"threshold": 1500, "name": "Proficient", "greek": "Επαρκής", "description": "Can discuss most topics", "unlock": "Story mode: A2"},
    {"threshold": 2000, "name": "Advanced", "greek": "Προχωρημένος", "description": "Fluent in daily life", "unlock": "News articles"},
    {"threshold": 3000, "name": "Expert", "greek": "Ειδικός", "description": "Near-native vocabulary", "unlock": "Literature excerpts"},
    {"threshold": 5000, "name": "Master", "greek": "Μάστορας", "description": "Comprehensive vocabulary", "unlock": "Full library access"},
]


def get_vocabulary_tier(words_known):
    """Get the current tier and progress to next."""
    current_tier = VOCABULARY_TIERS[0]
    next_tier = VOCABULARY_TIERS[1] if len(VOCABULARY_TIERS) > 1 else None
    
    for i, tier in enumerate(VOCABULARY_TIERS):
        if words_known >= tier["threshold"]:
            current_tier = tier
            next_tier = VOCABULARY_TIERS[i + 1] if i + 1 < len(VOCABULARY_TIERS) else None
    
    # Calculate progress to next tier
    if next_tier:
        progress_in_tier = words_known - current_tier["threshold"]
        tier_size = next_tier["threshold"] - current_tier["threshold"]
        progress_percent = min((progress_in_tier / tier_size) * 100, 100)
        words_to_next = next_tier["threshold"] - words_known
    else:
        progress_percent = 100
        words_to_next = 0
    
    return {
        "current": current_tier,
        "next": next_tier,
        "progress_percent": round(progress_percent, 1),
        "words_to_next": words_to_next
    }


def get_greek_coverage_estimate(words_known):
    """
    Estimate what percentage of everyday Greek the user can understand.
    Based on Zipf's law: most frequent words cover most of language use.
    """
    # Rough estimates based on corpus linguistics research
    if words_known >= 5000: return 98
    if words_known >= 3000: return 95
    if words_known >= 2000: return 90
    if words_known >= 1500: return 85
    if words_known >= 1000: return 80
    if words_known >= 500: return 65
    if words_known >= 250: return 50
    if words_known >= 100: return 30
    return min(words_known * 0.3, 30)


@bp.route('/comprehensive', methods=['GET'])
@login_required
def get_comprehensive_stats():
    """Get all dashboard metrics in one call."""
    try:
        user_id = session['user_id']
        now = datetime.utcnow()
        
        # ====================================================================
        # VOCABULARY METRICS
        # ====================================================================
        
        # Words by mastery level
        vocab_mastery = db.session.execute(
            db.text("""
                SELECT 
                    mastery_level,
                    COUNT(*) as count,
                    AVG(ease_factor) as avg_ease
                FROM user_vocabulary_progress 
                WHERE user_id = :user_id
                GROUP BY mastery_level
            """),
            {"user_id": user_id}
        ).fetchall()
        
        mastery_breakdown = {row[0]: {"count": row[1], "avg_ease": round(row[2] or 2.5, 2)} for row in vocab_mastery}
        
        # Calculate vocabulary categories
        words_active = sum(m["count"] for level, m in mastery_breakdown.items() if level >= 3)  # Mastery 3+ = active
        words_learning = sum(m["count"] for level, m in mastery_breakdown.items() if 1 <= level < 3)
        words_new = mastery_breakdown.get(0, {}).get("count", 0)
        total_words_known = sum(m["count"] for m in mastery_breakdown.values())
        
        # Words at risk (due in next 24 hours with low ease factor)
        words_at_risk = db.session.execute(
            db.text("""
                SELECT COUNT(*) FROM user_vocabulary_progress 
                WHERE user_id = :user_id 
                  AND next_review <= :tomorrow
                  AND ease_factor < 2.0
            """),
            {"user_id": user_id, "tomorrow": now + timedelta(hours=24)}
        ).fetchone()[0]
        
        # Words due now
        words_due = db.session.execute(
            db.text("""
                SELECT COUNT(*) FROM user_vocabulary_progress 
                WHERE user_id = :user_id AND next_review <= :now
            """),
            {"user_id": user_id, "now": now}
        ).fetchone()[0]
        
        # Words stabilized (high ease, long interval)
        words_stabilized = db.session.execute(
            db.text("""
                SELECT COUNT(*) FROM user_vocabulary_progress 
                WHERE user_id = :user_id 
                  AND ease_factor >= 2.5 
                  AND interval_days >= 21
            """),
            {"user_id": user_id}
        ).fetchone()[0]
        
        # Vocabulary accuracy
        vocab_stats = db.session.execute(
            db.text("""
                SELECT 
                    COALESCE(SUM(attempts), 0),
                    COALESCE(SUM(correct_attempts), 0)
                FROM user_vocabulary_progress 
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        ).fetchone()
        vocab_attempts = vocab_stats[0] or 0
        vocab_correct = vocab_stats[1] or 0
        vocab_accuracy = round((vocab_correct / vocab_attempts * 100) if vocab_attempts > 0 else 0, 1)
        
        # New words available
        new_available = db.session.execute(
            db.text("""
                SELECT COUNT(*) FROM common_words 
                WHERE id NOT IN (
                    SELECT word_id FROM user_vocabulary_progress WHERE user_id = :user_id
                )
            """),
            {"user_id": user_id}
        ).fetchone()[0]
        
        # Today's new words learned
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_new = db.session.execute(
            db.text("""
                SELECT COUNT(*) FROM user_vocabulary_progress 
                WHERE user_id = :user_id AND created_at >= :today
            """),
            {"user_id": user_id, "today": today_start}
        ).fetchone()[0]
        
        # ====================================================================
        # GRAMMAR/SKILL METRICS
        # ====================================================================
        
        # Get all skill progress
        skills = db.session.execute(
            db.text("""
                SELECT 
                    ucs.category,
                    csd.name,
                    csd.tier,
                    csd.tense,
                    csd.mood,
                    csd.voice,
                    ucs.attempts,
                    ucs.correct,
                    ucs.mastery_level
                FROM user_conjugation_skills ucs
                JOIN conjugation_skill_definitions csd ON ucs.category = csd.category
                WHERE ucs.user_id = :user_id
            """),
            {"user_id": user_id}
        ).fetchall()
        
        # Build skill rings data
        skill_domains = {}
        total_skill_attempts = 0
        total_skill_correct = 0
        
        for skill in skills:
            category, name, tier, tense, mood, voice, attempts, correct, mastery = skill
            
            # Group by domain (tense or special category)
            domain = tense if tense else "special"
            if domain not in skill_domains:
                skill_domains[domain] = {
                    "name": domain.title() if domain != "special" else "Special Forms",
                    "skills": [],
                    "total_mastery": 0,
                    "max_mastery": 0
                }
            
            skill_domains[domain]["skills"].append({
                "category": category,
                "name": name,
                "mastery_level": mastery,
                "attempts": attempts,
                "accuracy": round((correct / attempts * 100) if attempts > 0 else 0, 1)
            })
            skill_domains[domain]["total_mastery"] += mastery
            skill_domains[domain]["max_mastery"] += 5
            
            total_skill_attempts += attempts
            total_skill_correct += correct
        
        # Calculate domain progress percentages
        for domain in skill_domains.values():
            domain["progress"] = round(
                (domain["total_mastery"] / domain["max_mastery"] * 100) 
                if domain["max_mastery"] > 0 else 0, 1
            )
        
        skills_mastered = sum(1 for s in skills if s[8] >= 5)  # mastery_level index
        skills_proficient = sum(1 for s in skills if s[8] >= 3)
        total_skills = len(skills) if skills else 11  # Default to 11 if no skills yet
        
        # Weak skills (< 70% accuracy with 5+ attempts)
        weak_skills = [
            {"category": s[0], "name": s[1], "accuracy": round((s[7] / s[6] * 100) if s[6] > 0 else 0, 1)}
            for s in skills if s[6] >= 5 and (s[7] / s[6] * 100) < 70
        ]
        
        grammar_accuracy = round((total_skill_correct / total_skill_attempts * 100) if total_skill_attempts > 0 else 0, 1)
        
        # ====================================================================
        # OVERALL METRICS & GREEK COMPETENCY SCORE
        # ====================================================================
        
        # Weighted competency score (0-100)
        # 40% vocabulary coverage, 30% grammar mastery, 20% accuracy, 10% stability
        vocab_score = min(total_words_known / 20, 40)  # Max 40 points at 800 words
        grammar_score = (skills_proficient / max(total_skills, 1)) * 30  # Max 30 points
        accuracy_score = ((vocab_accuracy + grammar_accuracy) / 2) * 0.2  # Max 20 points
        stability_score = min(words_stabilized / 10, 10)  # Max 10 points at 100 stable words
        
        competency_score = round(vocab_score + grammar_score + accuracy_score + stability_score, 1)
        
        # Coverage estimate
        coverage_percent = get_greek_coverage_estimate(total_words_known)
        
        # Vocabulary tier
        tier_info = get_vocabulary_tier(total_words_known)
        
        # ====================================================================
        # DAILY QUESTS
        # ====================================================================
        
        # Today's reviews completed
        today_reviews = db.session.execute(
            db.text("""
                SELECT COUNT(*) FROM user_vocabulary_progress 
                WHERE user_id = :user_id 
                  AND last_attempt >= :today
            """),
            {"user_id": user_id, "today": today_start}
        ).fetchone()[0]
        
        quests = [
            {
                "id": "review_20",
                "name": "Daily Reviews",
                "description": "Review 20 vocabulary cards",
                "progress": min(today_reviews, 20),
                "target": 20,
                "completed": today_reviews >= 20,
                "xp": 50
            },
            {
                "id": "learn_5",
                "name": "Learn New Words",
                "description": "Learn 5 new vocabulary words",
                "progress": min(today_new, 5),
                "target": 5,
                "completed": today_new >= 5,
                "xp": 30
            },
            {
                "id": "grammar_practice",
                "name": "Grammar Practice",
                "description": "Complete 10 conjugation exercises",
                "progress": 0,  # Would need session tracking
                "target": 10,
                "completed": False,
                "xp": 40
            }
        ]
        
        # ====================================================================
        # NEXT BEST STEP RECOMMENDATION
        # ====================================================================
        
        recommendations = []
        
        # Priority 1: Words at risk
        if words_at_risk > 5:
            recommendations.append({
                "priority": 1,
                "type": "urgent",
                "title": f"{words_at_risk} words at risk of being forgotten",
                "action": "Review these words now to reinforce your memory",
                "button": "Review At-Risk Words",
                "route": "vocabulary"
            })
        
        # Priority 2: Due reviews
        if words_due > 10:
            recommendations.append({
                "priority": 2,
                "type": "important", 
                "title": f"{words_due} vocabulary reviews waiting",
                "action": "Stay on track with your spaced repetition",
                "button": "Start Reviews",
                "route": "vocabulary"
            })
        
        # Priority 3: Weak grammar skills
        if weak_skills:
            weakest = weak_skills[0]
            recommendations.append({
                "priority": 3,
                "type": "improve",
                "title": f"Your {weakest['name']} accuracy is {weakest['accuracy']}%",
                "action": "Practice this skill to improve your conjugations",
                "button": "Practice Now",
                "route": "conjugation",
                "skill": weakest['category']
            })
        
        # Priority 4: Learn new words (if caught up on reviews)
        if words_due < 5 and new_available > 0:
            words_to_next = tier_info["words_to_next"]
            if words_to_next > 0:
                recommendations.append({
                    "priority": 4,
                    "type": "grow",
                    "title": f"{words_to_next} words to reach {tier_info['next']['name'] if tier_info['next'] else 'max'} level",
                    "action": f"You understand ~{coverage_percent}% of everyday Greek",
                    "button": "Learn New Words",
                    "route": "vocabulary"
                })
        
        # Priority 5: Unlock new skill
        if skills_proficient > 0 and skills_proficient < total_skills:
            recommendations.append({
                "priority": 5,
                "type": "unlock",
                "title": "New grammar skills available",
                "action": "Master more conjugation patterns",
                "button": "View Skill Tree",
                "route": "progress"
            })
        
        # Sort by priority and take top recommendation
        recommendations.sort(key=lambda x: x["priority"])
        next_step = recommendations[0] if recommendations else {
            "priority": 10,
            "type": "celebrate",
            "title": "You're all caught up! 🎉",
            "action": "Great job staying on top of your learning",
            "button": "Explore More",
            "route": "home"
        }
        
        # ====================================================================
        # RETURN COMPREHENSIVE DATA
        # ====================================================================
        
        return jsonify({
            # Vocabulary
            "vocabulary": {
                "total_known": total_words_known,
                "active": words_active,
                "learning": words_learning,
                "new": words_new,
                "stabilized": words_stabilized,
                "at_risk": words_at_risk,
                "due": words_due,
                "new_available": new_available,
                "today_learned": today_new,
                "accuracy": vocab_accuracy,
                "mastery_breakdown": mastery_breakdown
            },
            
            # Coverage & Tiers
            "coverage": {
                "percent": coverage_percent,
                "tier": tier_info
            },
            
            # Grammar/Skills
            "grammar": {
                "skills_mastered": skills_mastered,
                "skills_proficient": skills_proficient,
                "total_skills": total_skills,
                "accuracy": grammar_accuracy,
                "domains": skill_domains,
                "weak_skills": weak_skills[:3]  # Top 3 weakest
            },
            
            # Overall
            "competency_score": competency_score,
            
            # Quests
            "quests": quests,
            
            # Recommendations
            "next_step": next_step,
            "all_recommendations": recommendations[:3],
            
            # Today's activity
            "today": {
                "reviews_completed": today_reviews,
                "words_learned": today_new
            }
        })
        
    except Exception as e:
        print(f"Error fetching dashboard: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch dashboard data'}), 500

