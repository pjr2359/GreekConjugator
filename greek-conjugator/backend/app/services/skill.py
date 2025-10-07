"""Utility functions for estimating user skill level."""

def calculate_skill_level(total_correct: int, accuracy_rate: float) -> int:
    """Estimate a user's skill level based on progress.

    Parameters
    ----------
    total_correct: int
        Total number of correct answers the user has given.
    accuracy_rate: float
        Overall accuracy percentage (0-100).

    Returns
    -------
    int
        Skill level from 1 (beginner) to 10 (expert).
    """
    # Experience grows with correct answers; accuracy provides a bonus.
    experience = total_correct // 10
    accuracy_bonus = int(accuracy_rate // 20)
    level = experience + accuracy_bonus + 1
    return max(1, min(level, 10))

