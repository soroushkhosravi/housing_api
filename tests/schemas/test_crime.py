"""Tests related to the crime schema."""
from schemas.crime import CrimeSchema
from models.crime import Crime

def test_schema_can_load_model():
    """Tests we can load a crime model from schema."""
    schema = CrimeSchema(many=True)
    crimes = schema.load(
        [
            {
                'category': 'anti-social-behaviour',
                'location_type': 'Force',
                'location': {
                    'latitude': '51.642425',
                    'street': {
                        'id': 1666896,
                        'name': 'On or near Connaught Road'
                    },
                    'longitude': '-0.209983'
                },
                'context': '',
                'outcome_status': None,
                'persistent_id': '',
                'id': 103280822,
                'location_subtype': '',
                'month': '2022-07'
            },
            {
                'category': 'anti-social-behaviour',
                'location_type': 'Force',
                'location': {
                    'latitude': '51.642425',
                    'street': {
                        'id': 1666896,
                        'name': 'On or near Connaught Road'
                    },
                    'longitude': '-0.209983'
                },
                'context': '',
                'outcome_status': None,
                'persistent_id': '',
                'id': 103280822,
                'location_subtype': '',
                'month': '2022-07'
            }
        ]
    )

    assert len(crimes) == 2