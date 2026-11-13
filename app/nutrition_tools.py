"""Public Nutrition API tools for FitPulse Coach.

Integrates with the free Fruityvice public API (from the public-apis catalog)
to fetch real-time nutritional and macronutrient data for foods and fruits.
"""

from __future__ import annotations

import os
from typing import Any
import httpx

FRUITYVICE_BASE_URL = os.getenv("FRUITYVICE_BASE_URL", "https://www.fruityvice.com/api/fruit")


def get_food_nutrition(food_item: str) -> dict[str, Any]:
    """Fetch verified nutritional and macronutrient data for a food or fruit item.

    Calls the free Fruityvice public API from the public-apis directory to retrieve
    calories, protein, carbohydrates, fat, and sugar per 100 grams.

    Args:
        food_item: Name of the whole food or fruit (e.g., 'banana', 'apple', 'avocado', 'strawberry', 'orange').

    Returns:
        A dictionary containing the nutritional breakdown per 100g or an error message if not found.
    """
    clean_name = food_item.strip().lower().split()[0]
    url = f"{FRUITYVICE_BASE_URL}/{clean_name}"

    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(url)
            if resp.status_code == 404:
                return {
                    "error": f"Nutritional data for '{food_item}' not found in the public database.",
                    "suggestion": "Try common whole foods and fruits like banana, apple, avocado, blueberry, orange, etc.",
                }
            resp.raise_for_status()
            data = resp.json()

        nutritions = data.get("nutritions", {})
        return {
            "food_item": data.get("name", food_item.title()),
            "family": data.get("family"),
            "serving_size": "100g",
            "per_100g": {
                "calories_kcal": nutritions.get("calories"),
                "protein_g": nutritions.get("protein"),
                "carbohydrates_g": nutritions.get("carbohydrates"),
                "fat_g": nutritions.get("fat"),
                "sugar_g": nutritions.get("sugar"),
            },
            "source": "Fruityvice Public API (public-apis directory)",
        }
    except Exception as e:
        return {"error": f"Failed to retrieve nutritional information: {e}"}
