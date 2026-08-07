import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# --- Eligibility Rule Schemas ---
class EligibilityRuleBase(BaseModel):
    min_cgpa: float = Field(0.0, ge=0.0, le=10.0)
    min_tenth_percentage: float = Field(0.0, ge=0.0, le=100.0)
    min_twelfth_percentage: float = Field(0.0, ge=0.0, le=100.0)
    allowed_branches: List[str] = Field(default_factory=list, description="e.g. ['CSE', 'IT']")
    max_active_backlogs: int = Field(0, ge=0)
    min_resume_match_score: int = Field(0, ge=0, le=100)


class EligibilityRuleCreate(EligibilityRuleBase):
    pass


class EligibilityRuleUpdate(BaseModel):
    min_cgpa: Optional[float] = None
    min_tenth_percentage: Optional[float] = None
    min_twelfth_percentage: Optional[float] = None
    allowed_branches: Optional[List[str]] = None
    max_active_backlogs: Optional[int] = None
    min_resume_match_score: Optional[int] = None


class EligibilityRuleResponse(EligibilityRuleBase):
    id: uuid.UUID
    role_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Skill Weights Schemas ---
class CompanySkillWeightBase(BaseModel):
    skill_name: str
    importance: int = Field(3, ge=1, le=5, description="Importance scale from 1 (low) to 5 (critical)")
    required_level: str = Field("Intermediate", description="Beginner, Intermediate, or Expert")


class CompanySkillWeightCreate(CompanySkillWeightBase):
    pass


class CompanySkillWeightResponse(CompanySkillWeightBase):
    id: uuid.UUID
    role_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Company Role Schemas ---
class CompanyRoleBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    ctc: float = Field(..., ge=0.0, description="CTC in LPA")
    description: Optional[str] = None
    application_link: Optional[str] = None
    difficulty: str = Field("Medium", description="Easy, Medium, or Hard")
    selection_rounds: int = Field(3, ge=1)
    hiring_pattern: Optional[str] = None
    expected_oa_pattern: Optional[str] = None
    technical_interview_topics: List[str] = Field(default_factory=list)
    hr_interview_topics: List[str] = Field(default_factory=list)
    interview_experience: Optional[str] = None
    preparation_resources: List[str] = Field(default_factory=list)


class CompanyRoleCreate(CompanyRoleBase):
    eligibility_rule: Optional[EligibilityRuleCreate] = None
    skill_weights: List[CompanySkillWeightCreate] = Field(default_factory=list)


class CompanyRoleUpdate(BaseModel):
    title: Optional[str] = None
    ctc: Optional[float] = None
    description: Optional[str] = None
    application_link: Optional[str] = None
    difficulty: Optional[str] = None
    selection_rounds: Optional[int] = None
    hiring_pattern: Optional[str] = None
    expected_oa_pattern: Optional[str] = None
    technical_interview_topics: Optional[List[str]] = None
    hr_interview_topics: Optional[List[str]] = None
    interview_experience: Optional[str] = None
    preparation_resources: Optional[List[str]] = None


class CompanyRoleResponse(CompanyRoleBase):
    id: uuid.UUID
    company_id: uuid.UUID
    eligibility_rule: Optional[EligibilityRuleResponse] = None
    skill_weights: List[CompanySkillWeightResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Company Schemas ---
class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    website_url: Optional[str] = None
    careers_url: Optional[str] = None
    industry: Optional[str] = None
    hq_location: Optional[str] = None
    hiring_frequency: str = "Yearly"
    internship_ppo_available: bool = True
    remote_onsite: str = "Onsite"
    data_source: str = "Admin Upload"


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    website_url: Optional[str] = None
    careers_url: Optional[str] = None
    industry: Optional[str] = None
    hq_location: Optional[str] = None
    hiring_frequency: Optional[str] = None
    internship_ppo_available: Optional[bool] = None
    remote_onsite: Optional[str] = None
    is_active: Optional[bool] = None


class CompanyResponse(CompanyBase):
    id: uuid.UUID
    last_updated: datetime
    is_active: bool
    roles: List[CompanyRoleResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Eligibility Evaluation Response ---
class EligibilityCheckResponse(BaseModel):
    is_eligible: bool
    overall_score: int = Field(..., ge=0, le=100)
    breakdown: Dict[str, int] = Field(..., description="Details for cgpa, branch, backlog, skills, and resume categories")
    reasons: List[str] = Field(default_factory=list, description="Descriptions of criteria that were not matched")
    missing_skills: List[Dict[str, Any]] = Field(default_factory=list, description="List of missing skills with weights")
    estimated_effort: str = Field("0 weeks", description="Calculated preparation time to resolve gaps")
