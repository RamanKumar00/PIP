from typing import Optional, Union, Dict, Any
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Retrieve a user record by email address.

        Args:
            db: SQLAlchemy Database Session.
            email: Email address of the user.

        Returns:
            Optional[User]: User object or None.
        """
        return db.query(self.model).filter(self.model.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Create a new user, hashing the password before saving.

        Args:
            db: SQLAlchemy Database Session.
            obj_in: Registration data schema.

        Returns:
            User: Created User instance.
        """
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            role="student",  # Default role
            is_active=True,
            is_verified=False,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """Update user details, hashing password if it is updated.

        Args:
            db: SQLAlchemy Database Session.
            db_obj: Existing User instance.
            obj_in: Update schema or dictionary.

        Returns:
            User: Updated User instance.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data["password"])
            del update_data["password"]
            
        return super().update(db, db_obj=db_obj, obj_in=update_data)


user_repo = UserRepository(User)
