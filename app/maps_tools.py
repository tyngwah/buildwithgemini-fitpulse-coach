"""Google Maps Platform Geocoding and Places (New) tools for FitPulse Coach.

Reads GOOGLE_MAPS_API_KEY from environment variables to avoid hardcoding secrets.
"""

from __future__ import annotations

import os
import urllib.parse
from typing import Any
from dotenv import load_dotenv
import httpx

load_dotenv()


def _get_api_key() -> str:
    key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
    if not key:
        raise ValueError(
            "GOOGLE_MAPS_API_KEY environment variable is not set. Please set it in your .env or environment."
        )
    return key


def geocode_address(address: str) -> dict[str, Any]:
    """Convert a human-readable street address, landmark, or city into geographical coordinates (latitude and longitude).

    Uses the Google Maps Geocoding REST API.

    Args:
        address: The address or location string to geocode (e.g., '1600 Amphitheatre Pkwy, Mountain View, CA' or 'Central Park, NY').

    Returns:
        A dictionary containing the formatted address, latitude, and longitude, or an error message if not found.
    """
    try:
        api_key = _get_api_key()
    except ValueError as e:
        return {"error": str(e)}

    encoded_address = urllib.parse.quote_plus(address.strip())
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()

        status = data.get("status")
        if status != "OK" or not data.get("results"):
            return {"error": f"Geocoding failed for '{address}': {status}", "raw": data}

        first_result = data["results"][0]
        location = first_result.get("geometry", {}).get("location", {})

        return {
            "formatted_address": first_result.get("formatted_address"),
            "location": {
                "latitude": location.get("lat"),
                "longitude": location.get("lng"),
            },
        }
    except Exception as e:
        return {"error": f"Failed to call Geocoding API: {e}"}


def search_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "gym",
    radius_meters: float = 5000.0,
    max_results: int = 5,
) -> dict[str, Any]:
    """Search for nearby places of a specified type (such as gyms, fitness centers, parks, or health food stores).

    Uses the Google Places API (New) searchNearby REST endpoint.

    Args:
        latitude: Center latitude coordinate for the search circle.
        longitude: Center longitude coordinate for the search circle.
        place_type: Place type to search for (e.g. 'gym', 'fitness_center', 'park', 'athletic_field'). Defaults to 'gym'.
        radius_meters: Search radius in meters (max 50000.0). Defaults to 5000.0 meters.
        max_results: Maximum number of places to return (between 1 and 20). Defaults to 5.

    Returns:
        A dictionary containing a list of places with name, formatted address, and location coordinates.
    """
    try:
        api_key = _get_api_key()
    except ValueError as e:
        return {"error": str(e)}

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
    }
    payload = {
        "includedTypes": [place_type.strip().lower()],
        "maxResultCount": min(max(1, max_results), 20),
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "radius": min(max(100.0, radius_meters), 50000.0),
            }
        },
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        results: list[dict[str, Any]] = []
        for p in data.get("places", []):
            display_name = p.get("displayName", {}).get("text", "Unknown Place")
            formatted_address = p.get("formattedAddress", "No address provided")
            loc = p.get("location", {})
            results.append({
                "name": display_name,
                "address": formatted_address,
                "location": {
                    "latitude": loc.get("latitude"),
                    "longitude": loc.get("longitude"),
                },
            })

        return {
            "place_type": place_type,
            "center": {"latitude": latitude, "longitude": longitude},
            "count": len(results),
            "places": results,
        }
    except Exception as e:
        return {"error": f"Failed to call Places API (New): {e}"}
