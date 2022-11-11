"""Tests related to the location model."""
from models.location import Location

def test_model_can_be_created():
    """."""
    location = Location(longitude=50, latitude=51)

    assert isinstance(location, Location)

    assert location.longitude == 50
    assert location.latitude == 51