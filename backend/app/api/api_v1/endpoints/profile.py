from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.repositories.profile import profile_repo

router = APIRouter()


@router.get("/", response_model=ProfileResponse)
def read_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Retrieve the profile details of the authenticated student.
    """
    profile = profile_repo.get_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please complete your profile.",
        )
    return profile


@router.put("/", response_model=ProfileResponse)
def save_profile(
    profile_in: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Upsert student profile details. 
    If profile doesn't exist, it creates one; if it exists, it updates.
    """
    profile = profile_repo.get_by_user_id(db, user_id=current_user.id)
    if not profile:
        # We need to ensure we have all required fields for creation when initializing
        # Pydantic validates this on ProfileCreate. We can check if all fields in ProfileCreate are present.
        try:
            # Re-validate with ProfileCreate schema using input dictionary + user_id
            create_data = ProfileCreate(**profile_in.model_dump())
            # Convert to DB dict
            db_data = create_data.model_dump()
            db_data["user_id"] = current_user.id
            profile = profile_repo.create(db, obj_in=db_data)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot initialize profile: missing required fields. Details: {e}",
            )
    else:
        # Update existing profile
        profile = profile_repo.update(db, db_obj=profile, obj_in=profile_in)
    return profile
