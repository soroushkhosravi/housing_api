"""The definition of the user repository."""
from infrastructure.database import db
from models.user import User

class UserRepository:
    """The definition of the user repository class."""
    _model = User
    def __init__(self, session=None):
        self._session = session

    def get_by_google_id(self, google_id: str):
        """Returns a  user by it's google ID."""
        return self._session.query(self._model).filter_by(google_id=google_id).first()

    def add(self, model):
        """Adds a model to the database."""
        self._session.add(model)

    def commit(self):
        """Commits a transaction."""
        self._session.commit()
