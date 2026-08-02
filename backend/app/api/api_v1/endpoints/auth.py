from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core.database import get_db
from app.schemas.user import Token, UserCreate, UserResponse
from app.services.auth import auth_service

router = APIRouter()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    """Register a new student account.
    """
    user = auth_service.register_user(db, user_in=user_in)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    return user


@router.post("/login", response_model=Token)
def login(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    """Login endpoint for external callers/frontend sending JSON.
    """
    user = auth_service.authenticate_user(
        db, email=user_in.email, password=user_in.password
    )
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect email or password"
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=400, detail="Inactive user"
        )
    return auth_service.generate_tokens(user_id=user.id)


@router.post("/login-swagger", response_model=Token)
def login_swagger(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, for Swagger UI validation.
    """
    user = auth_service.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect email or password"
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=400, detail="Inactive user"
        )
    return auth_service.generate_tokens(user_id=user.id)


@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)) -> Any:
    """Refresh access token using a valid refresh token.
    """
    new_tokens = auth_service.refresh_access_token(db, refresh_token=refresh_token)
    if not new_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    return new_tokens


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: UserResponse = Depends(deps.get_current_user)) -> Any:
    """Retrieve details of the currently authenticated user.
    """
    return current_user


@router.post("/logout")
def logout(current_user: UserResponse = Depends(deps.get_current_user)) -> Any:
    """Log out user and signal session termination.
    """
    return {"detail": "Successfully logged out"}
