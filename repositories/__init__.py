"""The definition of all the repositories."""
import requests

from repositories.crime import Crime


def get_crime_repository():
    """."""
    return Crime(http=requests)