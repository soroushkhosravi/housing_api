"""The repository responsible for finding the crime rates."""
import requests
import pgeocode
import numpy as np
from models.location import Location
from schemas.crime import CrimeSchema

class Crime:
    """The repository responsible for finding number of crimes."""

    UK_ISO_CODE = 'GB'

    def __init__(self, http):
        """Instantiates the class."""
        self._http = http

    def grab_location(self, postcode: str):
        """Grabs a location out of a postcode.

        Args:
            postcode: The postcode passed.

        Returns:
            A location having the longitude and latitude numbers.
        """
        query = pgeocode.Nominatim(self.UK_ISO_CODE).query_postal_code(postcode)
        location = None

        if not np.isnan(query.latitude) and not np.isnan(query.longitude):
            location = Location(
                latitude=float(query.latitude),
                longitude=float(query.longitude))

        return location

    def get_crimes(self, postcode, month, year):
        """Returns list of crimes for a specific postcode.

        Args:
            postcode: The postcode of the place.
            month: The month number.
            year: The year number.

        Returns:
            List of crimes happened in the place.
        """
        location = self.grab_location(postcode=postcode)

        if not location:
            return None
        response = self._http.get(
            f'https://data.police.uk/api/crimes-street/all-crime?lat={location.latitude}&'
            f'lng={location.longitude}&date={year}-{month}'
        )

        if response.status_code != 200:
            return []

        return CrimeSchema(many=True).load(response.json())



