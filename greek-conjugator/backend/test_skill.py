from app.services.skill import calculate_skill_level


def test_calculate_skill_level_progression():
    assert calculate_skill_level(0, 0) == 1
    beginner = calculate_skill_level(10, 50)
    advanced = calculate_skill_level(100, 80)
    assert beginner >= 1
    assert advanced > beginner

