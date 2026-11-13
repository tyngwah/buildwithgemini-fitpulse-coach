from app.fitness_tools import calculate_heart_rate_zones


def test_calculate_heart_rate_zones():
    res = calculate_heart_rate_zones(age=30, resting_heart_rate=60)
    assert res["athlete_age"] == 30
    assert res["max_heart_rate_bpm"] == 190
    assert res["heart_rate_reserve_bpm"] == 130
    assert "zone_2_aerobic_base" in res["training_zones"]
    assert "zone_5_anaerobic_max" in res["training_zones"]
