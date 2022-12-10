"""The definition of all the application services."""
from services.user import UserService
from repositories import get_user_repository

def get_user_service(users=None):
    """."""
    return UserService(users=users or get_user_repository())