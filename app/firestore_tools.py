"""Firestore backend tools for FitPulse Coach.

Hardcodes the GCP project ID as a string to avoid project number issues on Agent Platform.
"""

from __future__ import annotations

import datetime
import re
from typing import Any
from google.cloud import firestore

# Hardcode project ID as string as required by Agent Platform & Firestore
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-04-ec0b87ee001f"

_db: firestore.Client | None = None


def get_firestore_client() -> firestore.Client:
    """Returns a singleton Firestore client pinned to the hardcoded project ID."""
    global _db
    if _db is None:
        _db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    return _db


def list_exercises(category: str = "") -> list[dict[str, Any]]:
    """List available exercises from the exercise library, optionally filtered by category.

    Args:
        category: Optional category filter such as 'Strength', 'Cardio', 'Mobility', or 'Bodyweight'.
                  If empty or not provided, returns all exercises.

    Returns:
        A list of exercise dictionaries containing id, name, category, primary_muscle, difficulty, and equipment.
    """
    db = get_firestore_client()
    collection_ref = db.collection("exercises")
    docs = collection_ref.stream()

    exercises: list[dict[str, Any]] = []
    target_category = category.strip().lower()

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        if not target_category or data.get("category", "").lower() == target_category:
            exercises.append(data)

    return exercises


def get_exercise_details(exercise_name: str) -> dict[str, Any]:
    """Retrieve detailed movement breakdown, target muscles, equipment, and form instructions for an exercise.

    Args:
        exercise_name: The name or slug ID of the exercise (e.g., 'Barbell Back Squat', 'pull-up', 'Bench Press').

    Returns:
        A dictionary containing the exercise details or an error message if not found.
    """
    db = get_firestore_client()
    collection_ref = db.collection("exercises")

    # First try direct ID lookup
    normalized_id = re.sub(r"[^a-zA-Z0-9]+", "-", exercise_name.strip().lower()).strip("-")
    doc_ref = collection_ref.document(normalized_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data

    # Otherwise scan for matching name
    search_term = exercise_name.strip().lower()
    for item in collection_ref.stream():
        data = item.to_dict()
        data["id"] = item.id
        if search_term in data.get("name", "").lower() or search_term in data.get("id", "").lower():
            return data

    return {"error": f"Exercise '{exercise_name}' not found in the library."}


def add_exercise(
    name: str,
    category: str,
    primary_muscle: str,
    difficulty: str,
    equipment: str,
    instructions: str,
    recommended_reps: str,
) -> dict[str, Any]:
    """Add a new custom exercise movement to the Firestore exercise catalog.

    Args:
        name: The display name of the exercise (e.g. 'Dumbbell Incline Bench Press').
        category: Category (e.g. 'Strength', 'Cardio', 'Mobility', 'Bodyweight').
        primary_muscle: The main target muscle group (e.g. 'Upper Chest').
        difficulty: Level of difficulty ('Beginner', 'Intermediate', or 'Advanced').
        equipment: Required equipment (e.g. 'Dumbbells, Incline Bench').
        instructions: Step-by-step coaching cues and form instructions.
        recommended_reps: Recommended sets and rep ranges (e.g. '3-4 sets of 8-12 reps').

    Returns:
        A dictionary with the created exercise ID and confirmation status.
    """
    db = get_firestore_client()
    collection_ref = db.collection("exercises")

    doc_id = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    payload = {
        "id": doc_id,
        "name": name.strip(),
        "category": category.strip().title(),
        "primary_muscle": primary_muscle.strip().title(),
        "secondary_muscles": [],
        "difficulty": difficulty.strip().title(),
        "equipment": equipment.strip(),
        "instructions": instructions.strip(),
        "recommended_reps": recommended_reps.strip(),
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    collection_ref.document(doc_id).set(payload)
    return {"status": "success", "message": f"Added exercise '{name}' with ID '{doc_id}'", "exercise": payload}


def log_workout(
    exercise_name: str,
    sets: int,
    reps: int,
    weight_lbs: float,
    notes: str = "",
) -> dict[str, Any]:
    """Log a completed workout exercise with sets, reps, weight, and notes into Firestore.

    Args:
        exercise_name: Name of the exercise performed (e.g. 'Barbell Back Squat').
        sets: Number of completed sets.
        reps: Number of repetitions per set.
        weight_lbs: Weight lifted in pounds (0 for bodyweight exercises).
        notes: Optional workout notes or RPE (Rate of Perceived Exertion).

    Returns:
        A dictionary confirming the logged workout entry with its generated ID and timestamp.
    """
    db = get_firestore_client()
    collection_ref = db.collection("workout_logs")

    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    log_entry = {
        "exercise_name": exercise_name.strip(),
        "sets": sets,
        "reps": reps,
        "weight_lbs": weight_lbs,
        "notes": notes.strip(),
        "timestamp": timestamp,
    }

    _, doc_ref = collection_ref.add(log_entry)
    log_entry["id"] = doc_ref.id
    return {"status": "success", "message": f"Logged workout for {exercise_name}", "log": log_entry}


def get_recent_workout_logs(limit: int = 5) -> list[dict[str, Any]]:
    """Retrieve the most recent logged workout sessions from Firestore.

    Args:
        limit: Maximum number of recent workout entries to retrieve (default is 5).

    Returns:
        A list of recent workout log entries with exercise name, sets, reps, weight, and timestamp.
    """
    db = get_firestore_client()
    collection_ref = db.collection("workout_logs")
    query = collection_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit)

    logs: list[dict[str, Any]] = []
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        logs.append(data)

    return logs
