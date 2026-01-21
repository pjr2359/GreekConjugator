"""
Dashboard API - Comprehensive learning metrics and recommendations
"""

from flask import Blueprint, jsonify, session
from ..models import db
from .auth import login_required
from datetime import datetime, timedelta
import math

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


# ============================================================================
# VOCABULARY TIERS - Based on real Greek language learning research
# ============================================================================
VOCABULARY_TIERS = [
    {"threshold": 0, "name": "Beginner", "greek": "Αρχάριος", "description": "Just starting out"},
    {"threshold": 100, "name": "Tourist", "greek": "Τουρίστας", "description": "Basic survival phrases"},
    {"threshold": 250, "name": "Explorer", "greek": "Εξερευνητής", "description": "Can handle simple interactions"},
    {"threshold": 500, "name": "Conversant", "greek": "Συνομιλητής", "description": "Basic daily conversations"},
    {"threshold": 1000, "name": "Competent", "greek": "Ικανός", "description": "Comfortable in everyday situations"},
    {"threshold": 1500, "name": "Proficient", "greek": "Επαρκής", "description": "Can discuss most topics"},
    {"threshold": 2000, "name": "Advanced", "greek": "Προχωρημένος", "description": "Fluent in daily life"},
    {"threshold": 3000, "name": "Expert", "greek": "Ειδικός", "description": "Near-native vocabulary"},
    {"threshold": 5000, "name": "Master", "greek": "Μάστορας", "description": "Comprehensive vocabulary"},
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
    Modeled as a Zipf-like saturation curve with diminishing returns.
    """
    # Exponential saturation calibrated to:
    # - 1000 words ≈ 85% coverage
    # - 5000 words ≈ 98% coverage (asymptote)
    words = max(words_known or 0, 0)
    max_coverage = 98.0
    k = -math.log(1 - (85.0 / max_coverage)) / 1000.0
    coverage = max_coverage * (1 - math.exp(-k * words))
    return round(min(max(coverage, 0), max_coverage), 1)


def _validate_dashboard_payload(payload):
    """Validate dashboard payload for internal consistency."""
    errors = []

    vocab = payload.get("vocabulary", {})
    coverage = payload.get("coverage", {})
    grammar = payload.get("grammar", {})

    # Basic non-negative checks
    non_negative_fields = [
        "total_studied", "mastered", "known", "new", "unseen", "for_coverage",
        "due", "stabilized", "new_available", "today_learned"
    ]
    for field in non_negative_fields:
        value = vocab.get(field)
        if value is not None and value < 0:
            errors.append(f"vocabulary.{field} is negative ({value})")

    # Total studied should match breakdown
    total_studied = vocab.get("total_studied")
    breakdown_sum = sum(
        vocab.get(key, 0) for key in ("mastered", "known", "new", "unseen")
    )
    if total_studied is not None and total_studied != breakdown_sum:
        errors.append(
            f"vocabulary.total_studied ({total_studied}) != breakdown sum ({breakdown_sum})"
        )

    # for_coverage should equal mastered + known
    for_coverage = vocab.get("for_coverage")
    expected_for_coverage = (vocab.get("mastered", 0) + vocab.get("known", 0))
    if for_coverage is not None and for_coverage != expected_for_coverage:
        errors.append(
            f"vocabulary.for_coverage ({for_coverage}) != mastered+known ({expected_for_coverage})"
        )

    # Due should not exceed total studied
    due = vocab.get("due")
    if due is not None and total_studied is not None and due > total_studied:
        errors.append(
            f"vocabulary.due ({due}) > total_studied ({total_studied})"
        )

    # Coverage percent should be 0-100
    coverage_percent = coverage.get("percent")
    if coverage_percent is not None and not (0 <= coverage_percent <= 100):
        errors.append(f"coverage.percent out of range ({coverage_percent})")

    # Competency score should be 0-100
    competency_score = payload.get("competency_score")
    if competency_score is not None and not (0 <= competency_score <= 100):
        errors.append(f"competency_score out of range ({competency_score})")

    # Grammar domain progress should be 0-100 and internally consistent
    domains = grammar.get("domains", {})
    for domain_key, domain in domains.items():
        progress = domain.get("progress")
        total_mastery = domain.get("total_mastery")
        max_mastery = domain.get("max_mastery")
        if progress is not None and not (0 <= progress <= 100):
            errors.append(f"grammar.domains[{domain_key}].progress out of range ({progress})")
        if max_mastery:
            expected = round((total_mastery / max_mastery) * 100, 1)
            if progress is not None and abs(progress - expected) > 0.1:
                errors.append(
                    f"grammar.domains[{domain_key}].progress ({progress}) != expected ({expected})"
                )

    return errors


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
        
        # Calculate vocabulary categories (new structure)
        words_mastered = sum(m["count"] for level, m in mastery_breakdown.items() if level >= 3)  # Mastery 3+ = mastered
        words_known = sum(m["count"] for level, m in mastery_breakdown.items() if level == 2)  # Mastery 2 = known
        words_new = sum(m["count"] for level, m in mastery_breakdown.items() if level == 1)  # Mastery 1 = new/learning
        words_unseen = mastery_breakdown.get(0, {}).get("count", 0)  # Mastery 0 = never reviewed
        total_words_studied = sum(m["count"] for m in mastery_breakdown.values())
        
        # Words that count toward Greek coverage (level 2+)
        words_for_coverage = words_mastered + words_known
        
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
                    csd.display_name,
                    csd.tier,
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
            category, name, tier, attempts, correct, mastery = skill
            
            # Group by tier
            domain = f"tier_{tier}"
            if domain not in skill_domains:
                skill_domains[domain] = {
                    "name": f"Tier {tier}",
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
        
        skills_mastered = sum(1 for s in skills if s[5] >= 5)  # mastery_level is now index 5
        skills_proficient = sum(1 for s in skills if s[5] >= 3)
        total_skills = len(skills) if skills else 11  # Default to 11 if no skills yet
        
        # Weak skills (< 70% accuracy with 5+ attempts)
        # Indices: 0=category, 1=name, 2=tier, 3=attempts, 4=correct, 5=mastery
        weak_skills = [
            {"category": s[0], "name": s[1], "accuracy": round((s[4] / s[3] * 100) if s[3] > 0 else 0, 1)}
            for s in skills if s[3] >= 5 and (s[4] / s[3] * 100) < 70
        ]
        
        grammar_accuracy = round((total_skill_correct / total_skill_attempts * 100) if total_skill_attempts > 0 else 0, 1)
        
        # ====================================================================
        # OVERALL METRICS & GREEK COMPETENCY SCORE
        # ====================================================================
        
        # Weighted competency score (0-100)
        # 40% vocabulary coverage, 30% grammar mastery, 20% accuracy, 10% stability
        vocab_score = min(words_for_coverage / 20, 40)  # Max 40 points at 800 words (level 2+)
        grammar_score = (skills_proficient / max(total_skills, 1)) * 30  # Max 30 points
        accuracy_score = ((vocab_accuracy + grammar_accuracy) / 2) * 0.2  # Max 20 points
        stability_score = min(words_stabilized / 10, 10)  # Max 10 points at 100 stable words
        
        competency_score = round(vocab_score + grammar_score + accuracy_score + stability_score, 1)
        
        # Coverage estimate (based on level 2+ words only)
        coverage_percent = get_greek_coverage_estimate(words_for_coverage)
        
        # Vocabulary tier (based on level 2+ words)
        tier_info = get_vocabulary_tier(words_for_coverage)
        
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
        
        # Priority 1: Due reviews
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
        
        payload = {
            # Vocabulary
            "vocabulary": {
                "total_studied": total_words_studied,
                "mastered": words_mastered,  # Level 3+
                "known": words_known,  # Level 2
                "new": words_new,  # Level 1
                "unseen": words_unseen,  # Level 0
                "for_coverage": words_for_coverage,  # Level 2+ (used for Greek %)
                "due": words_due,
                "stabilized": words_stabilized,
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
        }

        validation_errors = _validate_dashboard_payload(payload)
        if validation_errors:
            print(f"Dashboard stats validation failed: {validation_errors}")
            return jsonify({
                "error": "Dashboard statistics failed validation",
                "details": validation_errors
            }), 500

        return jsonify(payload)
        
    except Exception as e:
        print(f"Error fetching dashboard: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch dashboard data'}), 500


