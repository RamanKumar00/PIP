import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Numeric, ForeignKey, DateTime, Uuid, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    college: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    university: Mapped[str] = mapped_column(String(255), nullable=False)
    branch: Mapped[str] = mapped_column(String(100), nullable=False)
    current_year: Mapped[int] = mapped_column(Integer, nullable=False)
    cgpa: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    tenth_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    twelfth_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    linkedin_url: Mapped[str] = mapped_column(String(255), nullable=True)
    github_url: Mapped[str] = mapped_column(String(255), nullable=True)
    portfolio_url: Mapped[str] = mapped_column(String(255), nullable=True)
    preferred_role: Mapped[str] = mapped_column(String(100), nullable=True)
    preferred_companies: Mapped[list] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=list, nullable=False
    )
    backlogs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    resume_url: Mapped[str] = mapped_column(String(512), nullable=True)
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
    user: Mapped["User"] = relationship("User", back_populates="profile")

    def get_completion_stats(self) -> dict:
        """Calculate profile completion percentage and identify missing fields.
        """
        fields_to_check = {
            "full_name": "Full Name",
            "phone": "Phone Number",
            "college": "College Name",
            "university": "University Name",
            "branch": "Branch",
            "current_year": "Current Year",
            "cgpa": "CGPA",
            "tenth_percentage": "10th Percentage",
            "twelfth_percentage": "12th Percentage",
            "linkedin_url": "LinkedIn Profile",
            "github_url": "GitHub Profile",
            "portfolio_url": "Portfolio Website",
            "preferred_role": "Preferred Role",
            "preferred_companies": "Preferred Companies",
            "resume_url": "Resume Upload"
        }
        completed = 0
        missing = []
        for field, label in fields_to_check.items():
            val = getattr(self, field, None)
            if field == "preferred_companies":
                if val and len(val) > 0:
                    completed += 1
                else:
                    missing.append(label)
            elif val is not None and str(val).strip() != "":
                completed += 1
            else:
                missing.append(label)
        
        percentage = int((completed / len(fields_to_check)) * 100)
        return {
            "completion_percentage": percentage,
            "missing_fields": missing
        }

    @property
    def completion_percentage(self) -> int:
        """Property returning the profile completeness percentage.
        """
        return self.get_completion_stats()["completion_percentage"]

    @property
    def missing_fields(self) -> list:
        """Property returning list of missing profile field labels.
        """
        return self.get_completion_stats()["missing_fields"]


