import uuid
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    formatting_score: int = Field(0, ge=0, le=20)
    grammar_score: int = Field(0, ge=0, le=20)
    keyword_score: int = Field(0, ge=0, le=20)
    project_score: int = Field(0, ge=0, le=20)
    experience_score: int = Field(0, ge=0, le=20)
    achievements_score: int = Field(0, ge=0, le=20)
    contact_score: int = Field(0, ge=0, le=10)


class StrengthMeter(BaseModel):
    quality_label: str = Field("Needs Improvement", description="e.g. Excellent, Good, Fair")
    stars: int = Field(1, ge=1, le=5)
    professionalism: int = Field(0, ge=0, le=100)
    readability: int = Field(0, ge=0, le=100)
    technical_strength: int = Field(0, ge=0, le=100)
    ats_compatibility: int = Field(0, ge=0, le=100)


class SuggestionItem(BaseModel):
    category: str = Field(..., description="e.g. project, experience, formatting")
    target: str = Field(..., description="The specific text block or project title being reviewed")
    current: str = Field(..., description="The raw bullet point from user's resume")
    suggested: str = Field(..., description="Concrete, metrics-driven improved recommendation")
    rationale: str = Field(..., description="The reason why this suggestion was generated")


class ProjectAnalysis(BaseModel):
    title: str
    score: int = Field(0, ge=0, le=100)
    suggestions: List[str] = Field(default_factory=list)


class CategorizedSkills(BaseModel):
    programming: List[str] = Field(default_factory=list)
    backend: List[str] = Field(default_factory=list)
    frontend: List[str] = Field(default_factory=list)
    database: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    cloud: List[str] = Field(default_factory=list)


class RoleMatch(BaseModel):
    role_name: str
    match_percentage: int = Field(0, ge=0, le=100)
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)


class ResumeAnalysisResponse(BaseModel):
    id: uuid.UUID
    resume_id: uuid.UUID
    status: str
    error_message: Optional[str] = None
    ats_score: int = 0
    detailed_breakdown: Optional[ScoreBreakdown] = Field(None, validation_alias="score_breakdown")
    strength_meter: Optional[StrengthMeter] = Field(None, validation_alias="strength_meter")
    overall_feedback: Optional[str] = None
    suggestions: List[SuggestionItem] = Field(default_factory=list)
    project_analyses: List[ProjectAnalysis] = Field(default_factory=list, validation_alias="project_analyses_list")
    detected_skills: Optional[CategorizedSkills] = None
    missing_skills: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    role_match: Optional[RoleMatch] = Field(None, validation_alias="role_match")
    recruiter_report: Dict = Field(default_factory=dict)
    semantic_analysis: Dict = Field(default_factory=dict)
    interview_preparation: Dict = Field(default_factory=dict)
    analytics_data: Dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResumeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    original_filename: str
    file_size: int
    mime_type: str
    version: int
    is_active: bool
    created_at: datetime
    analysis: Optional[ResumeAnalysisResponse] = None

    class Config:
        from_attributes = True


# Schema to check status in long-polling request
class AnalysisStatusResponse(BaseModel):
    resume_id: uuid.UUID
    status: str
    ats_score: Optional[int] = None
    error_message: Optional[str] = None
