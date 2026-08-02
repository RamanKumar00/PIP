import uuid
from typing import Any, Optional
from datetime import datetime, timezone
from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean, Text, JSON, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), default="application/pdf", nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="resumes")
    analysis: Mapped["ResumeAnalysis"] = relationship(
        "ResumeAnalysis", back_populates="resume", uselist=False, cascade="all, delete-orphan"
    )


class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("resumes.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False) # "pending", "processing", "completed", "failed"
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

    # ATS Categorized Scores
    ats_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    grammar_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    formatting_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    keyword_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    project_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    experience_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    role_match_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Detailed Analysis Data
    overall_feedback: Mapped[str] = mapped_column(Text, nullable=True)
    detailed_breakdown: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=dict, nullable=False
    )
    suggestions: Mapped[list] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=list, nullable=False
    )
    missing_skills: Mapped[list] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=list, nullable=False
    )
    missing_keywords: Mapped[list] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=list, nullable=False
    )
    detected_skills: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=dict, nullable=False
    )
    parsed_text: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    resume: Mapped["Resume"] = relationship("Resume", back_populates="analysis")

    @property
    def score_breakdown(self) -> Optional[dict]:
        """Fetch the score breakdown nested dictionary if formatting_score is present.
        """
        if not self.detailed_breakdown or "formatting_score" not in self.detailed_breakdown:
            return None
        return self.detailed_breakdown

    @property
    def strength_meter(self) -> Optional[dict]:
        """Fetch the strength meter stats nested dictionary.
        """
        if not self.detailed_breakdown or "strength_meter" not in self.detailed_breakdown:
            return None
        return self.detailed_breakdown.get("strength_meter")

    @property
    def role_match(self) -> Optional[dict]:
        """Fetch the target role matching results nested dictionary.
        """
        if not self.detailed_breakdown or "role_match" not in self.detailed_breakdown:
            return None
        return self.detailed_breakdown.get("role_match")

    @property
    def project_analyses_list(self) -> list:
        """Fetch the list of project evaluations and tips.
        """
        if not self.detailed_breakdown or "project_analyses" not in self.detailed_breakdown:
            return []
        return self.detailed_breakdown.get("project_analyses", [])

