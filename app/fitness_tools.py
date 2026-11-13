"""Fitness computation and assessment tools for FitPulse Coach."""

from __future__ import annotations
from typing import Any


def calculate_heart_rate_zones(age: int, resting_heart_rate: int = 60) -> dict[str, Any]:
    """Calculate customized target cardiovascular heart rate training zones using the Karvonen formula.

    Args:
        age: Age of the athlete in years (e.g., 28).
        resting_heart_rate: Resting heart rate in beats per minute (BPM), typically between 45 and 80. Defaults to 60.

    Returns:
        A dictionary containing max heart rate, heart rate reserve, and calculated BPM ranges for Zones 1 through 5.
    """
    if age < 10 or age > 110:
        return {"error": "Age must be between 10 and 110."}

    max_hr = 220 - age
    hrr = max_hr - resting_heart_rate

    def get_bpm(intensity: float) -> int:
        return round((hrr * intensity) + resting_heart_rate)

    zones = {
        "zone_1_active_recovery": {
            "bpm_range": f"{get_bpm(0.50)} - {get_bpm(0.60)} bpm",
            "intensity": "50% - 60%",
            "focus": "Warm-up, cool-down, active recovery, and gentle aerobic blood flow.",
        },
        "zone_2_aerobic_base": {
            "bpm_range": f"{get_bpm(0.60)} - {get_bpm(0.70)} bpm",
            "intensity": "60% - 70%",
            "focus": "Aerobic endurance, mitochondrial density, and optimal fat oxidation.",
        },
        "zone_3_tempo": {
            "bpm_range": f"{get_bpm(0.70)} - {get_bpm(0.80)} bpm",
            "intensity": "70% - 80%",
            "focus": "Aerobic capacity, stamina, and race-pace conditioning.",
        },
        "zone_4_lactate_threshold": {
            "bpm_range": f"{get_bpm(0.80)} - {get_bpm(0.90)} bpm",
            "intensity": "80% - 90%",
            "focus": "Lactate threshold buffering, high-intensity endurance, and hard intervals.",
        },
        "zone_5_anaerobic_max": {
            "bpm_range": f"{get_bpm(0.90)} - {max_hr} bpm",
            "intensity": "90% - 100%",
            "focus": "VO2 max power, sprinting, and maximum effort intervals.",
        },
    }

    return {
        "athlete_age": age,
        "resting_heart_rate_bpm": resting_heart_rate,
        "max_heart_rate_bpm": max_hr,
        "heart_rate_reserve_bpm": hrr,
        "training_zones": zones,
    }
