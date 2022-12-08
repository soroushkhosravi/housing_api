from repositories.user import UserRepository
from models.user import User
from sqlalchemy import create_engine
import pytest
from infrastructure.database import db
from sqlalchemy.orm import Session
from repositories import get_user_repository
import uuid

@pytest.fixture
def session():
    """."""
    engine = create_engine('sqlite://')
    db.Model.metadata.drop_all(engine)
    db.Model.metadata.create_all(engine)

    return Session(engine)

def test_adding_user(session):
    """."""
    repo = get_user_repository(db=session)
    repo.add(User(
        google_id = 'google_id',
        name='Soroush',
        email = 'a@a.com',
        profile_pic='picture.com'
    ))
    repo.commit()

    users = session.query(User).all()

    assert len(users) == 1

    added_user = users[0]

    assert isinstance(added_user.id, uuid.UUID)
    assert added_user.google_id == 'google_id'
    assert added_user.name == 'Soroush'
    assert added_user.email == 'a@a.com'
    assert added_user.profile_pic == 'picture.com'
