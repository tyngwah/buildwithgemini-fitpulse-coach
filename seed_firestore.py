"""Seed script for FitPulse Coach Firestore backend.

Hardcodes the GCP project ID as a string to avoid project number issues on Agent Platform.
"""

from google.cloud import firestore

# Hardcode project ID as string as required by Agent Platform & Firestore
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-04-ec0b87ee001f"

SEEDED_EXERCISES = [
    {
        "id": "barbell-back-squat",
        "name": "Barbell Back Squat",
        "category": "Strength",
        "primary_muscle": "Quadriceps",
        "secondary_muscles": ["Glutes", "Hamstrings", "Core"],
        "difficulty": "Intermediate",
        "equipment": "Barbell, Squat Rack",
        "instructions": (
            "Position bar across upper traps. Unrack, brace core, and break at hips and knees "
            "simultaneously. Descend until thighs are parallel to the floor, then drive up through midfoot."
        ),
        "recommended_reps": "3-5 sets of 5-8 reps",
    },
    {
        "id": "barbell-bench-press",
        "name": "Barbell Bench Press",
        "category": "Strength",
        "primary_muscle": "Chest",
        "secondary_muscles": ["Triceps", "Anterior Deltoids"],
        "difficulty": "Intermediate",
        "equipment": "Barbell, Flat Bench",
        "instructions": (
            "Lie flat on the bench, grip the bar slightly wider than shoulder-width, tuck elbows at 45 degrees, "
            "lower bar with control to mid-chest, then press upwards explosively."
        ),
        "recommended_reps": "3-4 sets of 6-10 reps",
    },
    {
        "id": "romanian-deadlift",
        "name": "Romanian Deadlift",
        "category": "Strength",
        "primary_muscle": "Hamstrings",
        "secondary_muscles": ["Glutes", "Lower Back", "Lats"],
        "difficulty": "Intermediate",
        "equipment": "Barbell or Dumbbells",
        "instructions": (
            "Stand tall holding weight in front of thighs. Soften knees, hinge at the hips sending glutes back "
            "while keeping spine neutral. Lower until hamstrings stretch, then squeeze glutes to return."
        ),
        "recommended_reps": "3-4 sets of 8-12 reps",
    },
    {
        "id": "pull-up",
        "name": "Pull-Up",
        "category": "Bodyweight",
        "primary_muscle": "Lats",
        "secondary_muscles": ["Biceps", "Upper Back", "Core"],
        "difficulty": "Intermediate",
        "equipment": "Pull-Up Bar",
        "instructions": (
            "Hang from bar with overhand grip just outside shoulder width. Engage scapula, pull elbows down "
            "towards ribs until chin clears bar, lower with control to full dead-hang."
        ),
        "recommended_reps": "3-4 sets of 6-10 reps",
    },
    {
        "id": "hiit-sprints",
        "name": "HIIT Treadmill Sprints",
        "category": "Cardio",
        "primary_muscle": "Cardiovascular / Full Body",
        "secondary_muscles": ["Calves", "Quads", "Hamstrings"],
        "difficulty": "Advanced",
        "equipment": "Treadmill or Track",
        "instructions": (
            "Warm up for 5 mins. Alternate 30 seconds of maximum effort sprinting with 60 seconds "
            "of walking or light jogging recovery for 8 to 10 rounds."
        ),
        "recommended_reps": "8-10 intervals of 30s sprint / 60s rest",
    },
    {
        "id": "worlds-greatest-stretch",
        "name": "World's Greatest Stretch",
        "category": "Mobility",
        "primary_muscle": "Hip Flexors / Thoracic Spine",
        "secondary_muscles": ["Hamstrings", "Glutes", "Shoulders"],
        "difficulty": "Beginner",
        "equipment": "Yoga Mat",
        "instructions": (
            "Step into a deep lunge with both hands inside front foot. Drop inside elbow towards instep, "
            "then rotate and extend arm towards ceiling, opening chest. Repeat on both sides."
        ),
        "recommended_reps": "2 sets of 5-8 reps per side",
    },
]


def seed_firestore():
    print(f"Connecting to Firestore with project: {FIRESTORE_PROJECT_ID}...")
    db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    collection_ref = db.collection("exercises")

    for item in SEEDED_EXERCISES:
        doc_id = item["id"]
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(item)
        print(f"  ✓ Seeded exercise: {item['name']} ({doc_id})")

    print(f"Successfully seeded {len(SEEDED_EXERCISES)} exercises into collection 'exercises'!")


if __name__ == "__main__":
    seed_firestore()
