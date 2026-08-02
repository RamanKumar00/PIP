import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


class ProfileBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    college: str = Field(..., min_length=2, max_length=255)
    university: str = Field(..., min_length=2, max_length=255)
    branch: str = Field(..., min_length=2, max_length=100)
    current_year: int = Field(..., ge=1, le=5)
    cgpa: float = Field(..., ge=0.0, le=10.0)
    tenth_percentage: float = Field(..., ge=0.0, le=100.0)
    twelfth_percentage: float = Field(..., ge=0.0, le=100.0)
    phone: str = Field(..., min_length=10, max_length=20)
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    preferred_role: Optional[str] = None
    preferred_companies: List[str] = Field(default_factory=list)
    backlogs: int = Field(default=0, ge=0)
    resume_url: Optional[str] = None

    @field_validator("linkedin_url", "github_url", "portfolio_url", "resume_url", mode="before")
    @classmethod
    def allow_empty_string_as_none(cls, v: Optional[str]) -> Optional[str]:
        if v == "":
            return None
        return v


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    college: Optional[str] = Field(None, min_length=2, max_length=255)
    university: Optional[str] = Field(None, min_length=2, max_length=255)
    branch: Optional[str] = Field(None, min_length=2, max_length=100)
    current_year: Optional[int] = Field(None, ge=1, le=5)
    cgpa: Optional[float] = Field(None, ge=0.0, le=10.0)
    tenth_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    twelfth_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    preferred_role: Optional[str] = None
    preferred_companies: Optional[List[str]] = None
    backlogs: Optional[int] = Field(None, ge=0)
    resume_url: Optional[str] = None


class ProfileResponse(ProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    completion_percentage: int = 0
    missing_fields: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
