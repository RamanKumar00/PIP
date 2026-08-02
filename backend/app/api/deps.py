from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.repositories.user import user_repo
from app.schemas.user import TokenPayload

# Points to the login token endpoint for swagger docs authed requests
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login-swagger"
)


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """Dependency helper that returns the authenticated current user.

    Args:
        db: Database Session.
        token: Extracted Bearer JWT string.

    Returns:
        User: Authenticated database user object.

    Raises:
        HTTPException: 401 if invalid credentials or user not found.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_type = payload.get("type")
        user_id = payload.get("sub")
        if token_type != "access" or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials - incorrect token type",
            )
        token_data = TokenPayload(sub=user_id, type=token_type)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials - signature expired or corrupt",
        )
        
    import uuid
    try:
        user_uuid = uuid.UUID(str(token_data.sub))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials - invalid user identifier format",
        )
        
    user = user_repo.get(db, id=user_uuid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency helper that locks endpoints to active admins only.

    Args:
        current_user: Currently logged in user.

    Returns:
        User: Logged in admin user object.

    Raises:
        HTTPException: 403 if user lacks admin privileges.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges",
        )
    return current_user
