"""Tests related to the crime model."""
from models.crime import Crime
from datetime import date

def test_model_creation():
    """Tests object can be created."""
    crime = Crime(category='Anti social behaviour', date=date(year=2020, month=10, day=15))

    assert isinstance(crime, Crime)

    assert crime.category == 'Anti social behaviour'
    assert crime.date == date(year=2020, month=10, day=15)