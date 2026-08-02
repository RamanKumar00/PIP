import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean, Text, JSON, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class LearningResource(Base):
    __tablename__ = "learning_resources"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    skill_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estimated_hours: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), default="Intermediate", nullable=False)  # Beginner/Intermediate/Expert
    prerequisites: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tags: Mapped[list] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=list, nullable=False
    )
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g. Udemy, YouTube, Coursera
    popularity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class RoadmapTask(Base):
    __tablename__ = "roadmap_tasks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    company_role_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("company_roles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    learning_resource_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("learning_resources.id", ondelete="SET NULL"), nullable=True
    )
    skill_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # Scale 1-5
    estimated_hours: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), default="Intermediate", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="Not Started", nullable=False)  # Not Started, In Progress, Completed
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

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
    user: Mapped["User"] = relationship("User", back_populates="roadmap_tasks")
    role: Mapped["CompanyRole"] = relationship("CompanyRole")
    resource: Mapped[Optional["LearningResource"]] = relationship("LearningResource")
    study_sessions: Mapped[List["StudySession"]] = relationship(
        "StudySession", back_populates="task", cascade="all, delete-orphan"
    )


class StudySession(Base):
    __tablename__ = "study_sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    roadmap_task_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("roadmap_tasks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    focus_score: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # Scale 1-5
    energy_level: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # Scale 1-5
    resource_used: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    session_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    task: Mapped["RoadmapTask"] = relationship("RoadmapTask", back_populates="study_sessions")
    user: Mapped["User"] = relationship("User")


class UserSkillProgress(Base):
    __tablename__ = "user_skill_progress"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    skill_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    confidence_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0 to 100
    mastery_level: Mapped[str] = mapped_column(String(50), default="Beginner", nullable=False)  # Beginner, Intermediate, Mastered
    source: Mapped[str] = mapped_column(String(100), default="Resume Parse", nullable=False)  # Resume Parse, Roadmap Task, Quiz

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
    user: Mapped["User"] = relationship("User", back_populates="skill_progress")


class QuestionBank(Base):
    __tablename__ = "question_bank"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    skill_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    topic: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    difficulty: Mapped[str] = mapped_column(String(50), default="Intermediate", nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Options list stored as JSON
    options: Mapped[list] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=list, nullable=False
    )
    correct_option: Mapped[str] = mapped_column(String(255), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    
    tags: Mapped[list] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=list, nullable=False
    )
    company: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)  # Company specific questions
    role: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class InterviewFeedback(Base):
    __tablename__ = "interview_feedback"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("question_bank.id", ondelete="CASCADE"), index=True, nullable=False
    )
    student_answer: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Score breakdowns
    technical_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    communication_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completeness_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    grammar_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    overall_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    ai_feedback: Mapped[str] = mapped_column(Text, nullable=False)
    weak_areas: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_reading: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    question: Mapped["QuestionBank"] = relationship("QuestionBank")
