"""Tests related to the user application service."""
from repositories.user import UserRepository
from models.user import User
from sqlalchemy import create_engine
import pytest
from infrastructure.database import db
from sqlalchemy.orm import Session
from repositories import get_user_repository
import uuid
from services import get_user_service, UserService

@pytest.fixture
def session():
    """."""
    engine = create_engine('sqlite://')
    db.Model.metadata.drop_all(engine)
    db.Model.metadata.create_all(engine)

    return Session(engine)

@pytest.fixture
def service(session):
    """."""
    return get_user_service(users=get_user_repository(db=session))

def test_user_service(service):
    """."""
    assert isinstance(service, UserService)

    existing_user = service.existing_google_user(
        unique_google_id='google_id',
        email='a@a.com',
        picture='www.picture',
        username='username'
    )

    assert isinstance(existing_user, User)

    assert existing_user.google_id == 'google_id'
    assert existing_user.email == 'a@a.com'
    assert existing_user.profile_pic == 'www.picture'
    assert existing_user.name == 'username'

def test_user_not_added_if_user_with_google_id_already_exist(service):
    """."""
    user = User(
        google_id='google_id',
        name='username',
        email='a@a.com',
        profile_pic='www.picture'
    )

    service._users.add(user)
    service._users.commit()

    user_id = user.id

    existing_user = service.existing_google_user(
        unique_google_id='google_id',
        email='a@a.com',
        picture='www.picture',
        username='username'
    )

    assert existing_user.id == user_id
    assert existing_user.name == user.name
    assert existing_user.email == user.email
    assert existing_user.name == user.name