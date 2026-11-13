from app.nutrition_tools import get_food_nutrition


def test_get_food_nutrition():
    data = get_food_nutrition("banana")
    assert "error" not in data
    assert data["food_item"] == "Banana"
    assert "per_100g" in data
    assert data["per_100g"]["calories_kcal"] > 0
    assert data["per_100g"]["carbohydrates_g"] > 0
