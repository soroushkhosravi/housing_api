"""Tests related to the crime repository."""
import pytest
from repositories import get_crime_repository
from models.location import Location

@pytest.fixture
def repo():
    """A fixture for the tests."""
    return get_crime_repository()


def test_grab_location_returns_expected_location_with_valid_postcode(repo):
    """Tests we can get the location."""
    location = repo.grab_location(postcode='HP1 2DD')

    assert isinstance(location, Location)

    assert location.longitude == -0.49158
    assert location.latitude == 51.7551

def test_none_is_returned_as_location_with_invalid_postcode(repo):
    """Tests we can get the location."""
    location = repo.grab_location(postcode='Invalid')

    assert location is None