from repositories.user import UserRepository
from models.user import User
from sqlalchemy import create_engine
import pytest
from infrastructure.database import db
from sqlalchemy.orm import Session

def raise_exception():
    raise Exception(db.Model.metadata.__dict__)

engine = create_engine('sqlite://')
db.Model.metadata.create_all(engine)
with Session(engine) as session:
    session.add(User(
        google_id = 'google_id',
        name='Soroush',
        email = 'a@a.com',
        profile_pic='picture.com'
    ))
    session.commit()

users = session.query(User).filter_by(google_id='google_id').all()

assert users[0].name == 'Soroush'

repo = UserRepository(session=session)

user = repo.get_by_google_id(google_id='google_id')

assert user.name == 'Soroush'


