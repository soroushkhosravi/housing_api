"""The repository responsible for finding the crime rates."""
import requests
import pgeocode
import numpy as np
from models.location import Location

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
            location = Location(latitude=query.latitude, longitude=query.longitude)

        return location



