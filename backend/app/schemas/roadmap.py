import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# --- Learning Resource Schemas ---
class LearningResourceBase(BaseModel):
    skill_name: str
    title: str
    url: str
    description: Optional[str] = None
    estimated_hours: int = 5
    difficulty: str = "Intermediate"
    prerequisites: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    source: Optional[str] = None
    popularity: int = 0


class LearningResourceCreate(LearningResourceBase):
    pass


class LearningResourceResponse(LearningResourceBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Study Session Schemas ---
class StudySessionBase(BaseModel):
    duration_minutes: int = Field(..., ge=1, description="Study duration in minutes")
    focus_score: int = Field(3, ge=1, le=5, description="Focus level from 1 to 5")
    energy_level: int = Field(3, ge=1, le=5, description="Energy level from 1 to 5")
    resource_used: Optional[str] = None
    notes: Optional[str] = None


class StudySessionCreate(StudySessionBase):
    pass


class StudySessionResponse(StudySessionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    roadmap_task_id: uuid.UUID
    session_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# --- Roadmap Task Schemas ---
class RoadmapTaskBase(BaseModel):
    skill_name: str
    title: str
    priority: int = 3
    estimated_hours: int = 5
    difficulty: str = "Intermediate"
    status: str = "Not Started"
    progress_percentage: int = 0
    completed_at: Optional[datetime] = None


class RoadmapTaskCreate(RoadmapTaskBase):
    company_role_id: uuid.UUID
    learning_resource_id: Optional[uuid.UUID] = None


class RoadmapTaskResponse(RoadmapTaskBase):
    id: uuid.UUID
    user_id: uuid.UUID
    company_role_id: uuid.UUID
    learning_resource_id: Optional[uuid.UUID] = None
    resource: Optional[LearningResourceResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- User Skill Progress Schemas ---
class UserSkillProgressBase(BaseModel):
    skill_name: str
    confidence_score: int = Field(0, ge=0, le=100)
    mastery_level: str = "Beginner"  # Beginner, Intermediate, Mastered
    source: str = "Resume Parse"


class UserSkillProgressResponse(UserSkillProgressBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Question Bank Schemas ---
class QuestionBankBase(BaseModel):
    skill_name: str
    topic: Optional[str] = None
    difficulty: str = "Intermediate"
    question_text: str
    options: List[str] = Field(default_factory=list)
    correct_option: str
    explanation: str
    tags: List[str] = Field(default_factory=list)
    company: Optional[str] = None
    role: Optional[str] = None


class QuestionBankResponse(QuestionBankBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


# --- Mock Interview Schemas ---
class InterviewAnswerRequest(BaseModel):
    student_answer: str = Field(..., min_length=10)


class InterviewFeedbackResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    question_id: uuid.UUID
    student_answer: str
    technical_score: int
    communication_score: int
    completeness_score: int
    grammar_score: int
    overall_score: int
    ai_feedback: str
    weak_areas: str
    suggested_reading: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- Dashboard Analytics Console Schemas ---
class StudentDashboardMetrics(BaseModel):
    placement_readiness_percentage: int
    resume_ats_score: int
    study_streak_days: int
    total_study_hours: float
    roadmap_tasks_completed: int
    roadmap_tasks_total: int
    top_missing_skills: List[str] = Field(default_factory=list)
    eligible_companies_count: int
    almost_eligible_companies_count: int
    recommended_next_action: Optional[str] = None
    readiness_trend: Dict[str, int] = Field(default_factory=dict)
