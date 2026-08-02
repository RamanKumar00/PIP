import uuid
from typing import Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, Boolean, Text, JSON, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    website_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    careers_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    hq_location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    hiring_frequency: Mapped[str] = mapped_column(String(50), default="Yearly", nullable=False)
    internship_ppo_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    remote_onsite: Mapped[str] = mapped_column(String(50), default="Onsite", nullable=False)
    data_source: Mapped[str] = mapped_column(String(50), default="Admin Upload", nullable=False)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
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
    roles: Mapped[List["CompanyRole"]] = relationship(
        "CompanyRole", back_populates="company", cascade="all, delete-orphan"
    )


class CompanyRole(Base):
    __tablename__ = "company_roles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    ctc: Mapped[float] = mapped_column(Float, nullable=False)  # CTC in LPA
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    application_link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    difficulty: Mapped[str] = mapped_column(String(50), default="Medium", nullable=False)
    selection_rounds: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    hiring_pattern: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_oa_pattern: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Store topics list
    technical_interview_topics: Mapped[list] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=list, nullable=False
    )
    hr_interview_topics: Mapped[list] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=list, nullable=False
    )
    interview_experience: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Store prep resources
    preparation_resources: Mapped[list] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=list, nullable=False
    )

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
    company: Mapped["Company"] = relationship("Company", back_populates="roles")
    eligibility_rule: Mapped["EligibilityRule"] = relationship(
        "EligibilityRule", back_populates="role", uselist=False, cascade="all, delete-orphan"
    )
    skill_weights: Mapped[List["CompanySkillWeight"]] = relationship(
        "CompanySkillWeight", back_populates="role", cascade="all, delete-orphan"
    )


class EligibilityRule(Base):
    __tablename__ = "eligibility_rules"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    role_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("company_roles.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    min_cgpa: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    min_tenth_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    min_twelfth_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    # List of allowed branches, e.g. ["CSE", "IT", "ECE"]
    allowed_branches: Mapped[list] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=list, nullable=False
    )
    max_active_backlogs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    min_resume_match_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

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
    role: Mapped["CompanyRole"] = relationship("CompanyRole", back_populates="eligibility_rule")


class CompanySkillWeight(Base):
    __tablename__ = "company_skill_weights"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    role_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("company_roles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    skill_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    importance: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # Scale 1-5
    required_level: Mapped[str] = mapped_column(String(50), default="Intermediate", nullable=False)  # Beginner/Intermediate/Expert

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
    role: Mapped["CompanyRole"] = relationship("CompanyRole", back_populates="skill_weights")
