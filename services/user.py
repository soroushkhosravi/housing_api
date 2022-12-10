"""The definition of the user application service."""
from models.user import User

class UserService:
    def __init__(self, users):
        """."""
        self._users = users

    def existing_google_user(
            self,
            unique_google_id,
            email,
            picture,
            username
    ):
        """Returns the existing google user."""
        existing_user = self._users.get_by_google_id(google_id=unique_google_id)

        if not existing_user:
            existing_user = User(
                google_id=unique_google_id,
                name=username,
                email=email,
                profile_pic=picture
            )
            self._users.add(existing_user)
            self._users.commit()

        return existing_user