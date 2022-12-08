"""The definition of all the repositories."""
import requests

from repositories.crime import Crime
from repositories.user import UserRepository
from infrastructure.database import db as default_db


def get_crime_repository():
    """."""
    return Crime(http=requests)

def get_user_repository(db=None):
    """A factory for creating repository."""
    return UserRepository(session=db or default_db.session)