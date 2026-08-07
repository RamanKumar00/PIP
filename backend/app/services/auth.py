from datetime import datetime, timezone
from typing import Optional
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.models.user import User
from app.repositories.user import user_repo
from app.schemas.user import Token, UserCreate


class AuthService:
    def authenticate_user(
        self, db: Session, email: str, password: str
    ) -> Optional[User]:
        """Authenticate user by checking email and verifying password hash.

        Args:
            db: SQLAlchemy Database Session.
            email: User's email.
            password: User's plain password.

        Returns:
            Optional[User]: User model instance if authenticated, else None.
        """
        user = user_repo.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def register_user(self, db: Session, user_in: UserCreate) -> Optional[User]:
        """Register a new student, verifying email uniqueness.

        Args:
            db: SQLAlchemy Database Session.
            user_in: Registration data schema.

        Returns:
            Optional[User]: Created user if successful, None if email already exists.
        """
        existing_user = user_repo.get_by_email(db, email=user_in.email)
        if existing_user:
            return None
        return user_repo.create(db, obj_in=user_in)

    def generate_tokens(self, user_id: str) -> Token:
        """Generate access and refresh tokens for a user ID.

        Args:
            user_id: User's unique ID.

        Returns:
            Token: Token schema containing JWT strings.
        """
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    def refresh_access_token(self, db: Session, refresh_token: str) -> Optional[Token]:
        """Validate refresh token and issue a new access token.

        Args:
            db: SQLAlchemy Database Session.
            refresh_token: The user's refresh JWT token.

        Returns:
            Optional[Token]: New tokens schema if valid, else None.
        """
        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            token_type = payload.get("type")
            user_id = payload.get("sub")
            if token_type != "refresh" or not user_id:
                return None
        except JWTError:
            return None

        # Verify user still exists and is active
        import uuid
        try:
            user_uuid = uuid.UUID(str(user_id))
        except (ValueError, TypeError):
            return None

        user = user_repo.get(db, id=user_uuid)
        if not user or not user.is_active:
            return None

        # Re-generate both tokens
        return self.generate_tokens(user_id=user.id)


auth_service = AuthService()
