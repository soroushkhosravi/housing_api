"""The definition of the user model."""
from infrastructure.database import db
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    google_id = db.Column(db.String)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    profile_pic = db.Column(db.String, nullable=False)