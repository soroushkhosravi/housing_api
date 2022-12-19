"""The definition of the user model."""
import uuid
import uuid
from infrastructure.database import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TypeDecorator, CHAR


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    google_id = db.Column(db.String)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    profile_pic = db.Column(db.String, nullable=False)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class MyAnonymousUser:
    """Class for defining the anonymous user in not logged in endpoints."""

    def __init__(self):
        self.id = None
        self.google_id = None
        self.name = 'Guest'
        self.email = None
        self.profile_pic = None

    @property
    def is_active(self):
        return False

    @property
    def is_authenticated(self):
        return False

    @property
    def is_anonymous(self):
        return True

    def get_id(self):
        return None