from app.maps_tools import geocode_address, search_nearby_places


def test_geocode_address():
    res = geocode_address("1600 Amphitheatre Pkwy, Mountain View, CA")
    assert "error" not in res
    assert "location" in res
    assert res["location"]["latitude"] is not None
    assert res["location"]["longitude"] is not None


def test_search_nearby_places():
    res = search_nearby_places(37.4224864, -122.0855962, place_type="gym", radius_meters=5000, max_results=3)
    assert "error" not in res
    assert "places" in res
    assert len(res["places"]) > 0
    assert "name" in res["places"][0]
    assert "address" in res["places"][0]
    assert "location" in res["places"][0]
