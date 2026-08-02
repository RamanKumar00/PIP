from typing import Any, Optional
from sqlalchemy.orm import Session

from app.models.profile import Profile
from app.repositories.base import BaseRepository


class ProfileRepository(BaseRepository[Profile]):
    def get_by_user_id(self, db: Session, *, user_id: Any) -> Optional[Profile]:
        """Retrieve the profile associated with a specific user ID.

        Args:
            db: SQLAlchemy Database Session.
            user_id: ID of the user.

        Returns:
            Optional[Profile]: Profile instance if found, else None.
        """
        return db.query(self.model).filter(self.model.user_id == user_id).first()


profile_repo = ProfileRepository(Profile)
