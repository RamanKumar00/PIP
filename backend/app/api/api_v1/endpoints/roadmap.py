import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.models.profile import Profile
from app.models.resume import Resume
from app.models.company import Company, CompanyRole, EligibilityRule, CompanySkillWeight
from app.models.roadmap import (
    LearningResource, 
    RoadmapTask, 
    StudySession, 
    UserSkillProgress, 
    QuestionBank, 
    InterviewFeedback
)
from app.schemas.roadmap import (
    RoadmapTaskResponse,
    StudySessionCreate,
    StudySessionResponse,
    QuestionBankResponse,
    InterviewAnswerRequest,
    InterviewFeedbackResponse,
    StudentDashboardMetrics,
    UserSkillProgressResponse
)
from app.services.eligibility.engine import evaluate_eligibility

router = APIRouter()


@router.post("/generate/{role_id}", response_model=List[RoadmapTaskResponse])
def generate_roadmap_for_role(
    role_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Evaluate target role skill gaps and generate a personalized learning roadmap.
    """
    # 1. Fetch Company Role
    role = db.query(CompanyRole).filter(CompanyRole.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job role not found.",
        )

    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    resume = db.query(Resume).filter(Resume.user_id == current_user.id, Resume.is_active == True).first()

    # 2. Evaluate skill gap
    evaluation = evaluate_eligibility(
        profile=profile,
        active_resume=resume,
        rule=role.eligibility_rule,
        skill_weights=role.skill_weights,
        db=db,
    )

    missing_skills = evaluation.get("missing_skills", [])
    generated_tasks = []

    # Map skill importance to priority values
    # Sort missing skills by importance (prerequisites priority)
    missing_skills = sorted(missing_skills, key=lambda x: x["importance"], reverse=True)

    for skill in missing_skills:
        skill_name = skill["skill_name"]
        importance = skill["importance"]
        level = skill["required_level"]

        # Check if task already exists for this user, role, and skill
        existing_task = (
            db.query(RoadmapTask)
            .filter(
                RoadmapTask.user_id == current_user.id,
                RoadmapTask.company_role_id == role.id,
                RoadmapTask.skill_name.ilike(skill_name)
            )
            .first()
        )
        if existing_task:
            generated_tasks.append(existing_task)
            continue

        # Look up curated learning resources in database
        resources = (
            db.query(LearningResource)
            .filter(LearningResource.skill_name.ilike(skill_name))
            .all()
        )

        if resources:
            # Create a task for each resource
            for res in resources:
                task = RoadmapTask(
                    user_id=current_user.id,
                    company_role_id=role.id,
                    learning_resource_id=res.id,
                    skill_name=skill_name,
                    title=f"Master {skill_name}: {res.title}",
                    priority=importance,
                    estimated_hours=res.estimated_hours,
                    difficulty=res.difficulty,
                    status="Not Started",
                    progress_percentage=0,
                )
                db.add(task)
                generated_tasks.append(task)
        else:
            # Create fallback general study task
            task = RoadmapTask(
                user_id=current_user.id,
                company_role_id=role.id,
                skill_name=skill_name,
                title=f"Master basics of {skill_name} ({level} level)",
                priority=importance,
                estimated_hours=10,
                difficulty=level,
                status="Not Started",
                progress_percentage=0,
            )
            db.add(task)
            generated_tasks.append(task)

        # Initialize UserSkillProgress for this skill if not exists
        existing_progress = (
            db.query(UserSkillProgress)
            .filter(
                UserSkillProgress.user_id == current_user.id,
                UserSkillProgress.skill_name.ilike(skill_name)
            )
            .first()
        )
        if not existing_progress:
            skill_progress = UserSkillProgress(
                user_id=current_user.id,
                skill_name=skill_name,
                confidence_score=0,
                mastery_level="Beginner",
                source="Roadmap Task"
            )
            db.add(skill_progress)

    db.commit()
    return generated_tasks


@router.get("/tasks", response_model=List[RoadmapTaskResponse])
def get_roadmap_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Retrieve all study roadmap tasks for the student.
    """
    tasks = (
        db.query(RoadmapTask)
        .filter(RoadmapTask.user_id == current_user.id)
        .order_by(RoadmapTask.priority.desc(), RoadmapTask.skill_name.asc())
        .all()
    )
    return tasks


@router.put("/tasks/{task_id}/status", response_model=RoadmapTaskResponse)
def update_task_status(
    task_id: uuid.UUID,
    status_str: str,  # "Not Started", "In Progress", "Completed"
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Toggle study task status, adjusting skill confidence and triggering closed-loop eligibility recalculations.
    """
    task = db.query(RoadmapTask).filter(RoadmapTask.id == task_id, RoadmapTask.user_id == current_user.id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap task not found.",
        )

    old_status = task.status
    task.status = status_str
    if status_str == "Completed" and old_status != "Completed":
        task.completed_at = datetime.now(timezone.utc)
        task.progress_percentage = 100

        # Evolving Skill Proficiency: completing task yields +30% confidence boost
        progress = (
            db.query(UserSkillProgress)
            .filter(
                UserSkillProgress.user_id == current_user.id,
                UserSkillProgress.skill_name.ilike(task.skill_name)
            )
            .first()
        )
        if not progress:
            progress = UserSkillProgress(
                user_id=current_user.id,
                skill_name=task.skill_name,
                confidence_score=0,
                mastery_level="Beginner",
                source="Roadmap Task"
            )
            db.add(progress)

        progress.confidence_score = min(progress.confidence_score + 30, 100)
        
        # Determine mastery tags
        if progress.confidence_score >= 80:
            progress.mastery_level = "Mastered"
        elif progress.confidence_score >= 50:
            progress.mastery_level = "Intermediate"
        else:
            progress.mastery_level = "Beginner"

        progress.updated_at = datetime.now(timezone.utc)
        
    elif status_str != "Completed":
        task.completed_at = None
        if status_str == "Not Started":
            task.progress_percentage = 0

    db.commit()
    db.refresh(task)
    return task


@router.post("/tasks/{task_id}/study-sessions", response_model=StudySessionResponse)
def log_study_session(
    task_id: uuid.UUID,
    session_in: StudySessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Log study hours, updating the task progress percentage.
    """
    task = db.query(RoadmapTask).filter(RoadmapTask.id == task_id, RoadmapTask.user_id == current_user.id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap task not found.",
        )

    # 1. Create Session Log
    session = StudySession(
        user_id=current_user.id,
        roadmap_task_id=task_id,
        duration_minutes=session_in.duration_minutes,
        focus_score=session_in.focus_score,
        energy_level=session_in.energy_level,
        resource_used=session_in.resource_used,
        notes=session_in.notes,
    )
    db.add(session)

    # 2. Update task progress percentage
    # (Scale progress by duration vs estimated hours)
    added_progress = int((session_in.duration_minutes / (task.estimated_hours * 60)) * 100)
    task.progress_percentage = min(task.progress_percentage + max(added_progress, 10), 99)
    task.status = "In Progress"

    db.commit()
    db.refresh(session)
    return session


@router.get("/quizzes/{skill_name}", response_model=List[QuestionBankResponse])
def get_practice_quizzes(
    skill_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Fetch MCQ practice questions from the question bank. Falls back to generating dynamic ones.
    """
    questions = (
        db.query(QuestionBank)
        .filter(QuestionBank.skill_name.ilike(skill_name))
        .limit(5)
        .all()
    )
    
    if not questions:
        # Seed dynamic fallback questions for common topics so the user always has a quiz
        fallback_questions = [
            {
                "id": uuid.uuid4(),
                "skill_name": skill_name,
                "topic": "Fundamentals",
                "difficulty": "Medium",
                "question_text": f"Which of the following describes the primary benefit of deploying applications with {skill_name}?",
                "options": [
                    "Guarantees 100% bug-free compilation execution.",
                    "Provides process isolation, environment consistency, and scalability.",
                    "Replaces the need for writing unit tests.",
                    "Speeds up network requests automatically."
                ],
                "correct_option": "Provides process isolation, environment consistency, and scalability.",
                "explanation": f"Using {skill_name} ensures environment configurations remain identical from dev to production, isolated inside namespaces.",
                "tags": ["core", "deployment"],
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": uuid.uuid4(),
                "skill_name": skill_name,
                "topic": "Architecture",
                "difficulty": "Hard",
                "question_text": f"When configuring {skill_name} in enterprise pipelines, what is the best practice for caching packages?",
                "options": [
                    "Download dependencies on every single run.",
                    "Utilize volume mounts or layers caching during compilation.",
                    "Commit dependency binaries to the Git repository.",
                    "Disable compilation caches completely."
                ],
                "correct_option": "Utilize volume mounts or layers caching during compilation.",
                "explanation": "Caching build layers dramatically cuts down integration runner times.",
                "tags": ["ci-cd", "optimization"],
                "created_at": datetime.now(timezone.utc)
            }
        ]
        return fallback_questions

    return questions


@router.post("/interviews/{question_id}/answer", response_model=InterviewFeedbackResponse)
def submit_interview_answer(
    question_id: uuid.UUID,
    answer_in: InterviewAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Evaluate student's mock interview answers, scoring accuracy, grammar, and completeness.
    """
    question = db.query(QuestionBank).filter(QuestionBank.id == question_id).first()
    # Mock fallback check if uuid not in DB
    q_text = "Standard Question"
    skill = "Docker"
    if question:
        q_text = question.question_text
        skill = question.skill_name

    ans_lower = answer_in.student_answer.lower()
    
    # 1. Technical completeness check (simulate LLM matching terms)
    keywords = ["container", "image", "isolation", "dockerfile", "volume", "compose", "api", "query", "fastapi", "dsa", "complexity", "index"]
    matches = [k for k in keywords if k in ans_lower]
    
    tech_score = 50 + len(matches) * 10
    tech_score = min(max(tech_score, 45), 98)

    # 2. Grammar & Communication scores
    comm_score = min(max(60 + len(answer_in.student_answer) // 10, 50), 95)
    completeness = min(max(40 + len(matches) * 12, 40), 96)
    grammar_score = 85 if "the" in ans_lower else 70
    
    overall = int((tech_score * 0.4) + (comm_score * 0.2) + (completeness * 0.2) + (grammar_score * 0.2))

    # Compile feedback text
    feedback = f"Good attempt at explaining {skill}. You demonstrated solid conceptual familiarity. "
    if len(matches) < 2:
        feedback += "However, your explanation was very brief. To score higher in actual placement panels, try to mention implementation details like containers, environment variables, or caching mechanisms."
        weak_areas = "Implementation specifics, engineering vocabulary"
        suggested_reading = f"https://www.google.com/search?q={skill}+production+best+practices"
    else:
        feedback += f"You successfully integrated key terms: {', '.join(matches[:3])}. This shows good practical exposure."
        weak_areas = "Advanced architecture scaling options"
        suggested_reading = f"https://www.google.com/search?q={skill}+advanced+concepts"

    # Save practice feedback
    fb_record = InterviewFeedback(
        user_id=current_user.id,
        question_id=question_id if question else uuid.uuid4(),
        student_answer=answer_in.student_answer,
        technical_score=tech_score,
        communication_score=comm_score,
        completeness_score=completeness,
        grammar_score=grammar_score,
        overall_score=overall,
        ai_feedback=feedback,
        weak_areas=weak_areas,
        suggested_reading=suggested_reading,
    )
    
    # Also if overall score >= 75, give a small confidence boost (+10%) to the skill progress!
    if overall >= 75:
        progress = db.query(UserSkillProgress).filter(
            UserSkillProgress.user_id == current_user.id,
            UserSkillProgress.skill_name.ilike(skill)
        ).first()
        if progress:
            progress.confidence_score = min(progress.confidence_score + 10, 100)
            if progress.confidence_score >= 80:
                progress.mastery_level = "Mastered"
            db.commit()

    db.add(fb_record)
    db.commit()
    db.refresh(fb_record)
    return fb_record


@router.get("/dashboard-analytics", response_model=StudentDashboardMetrics)
def get_dashboard_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Compile student homepage analytics, readiness indicators, and study session streak graphs.
    """
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    resume = db.query(Resume).filter(Resume.user_id == current_user.id, Resume.is_active == True).first()

    # 1. Fetch all company roles
    roles = db.query(CompanyRole).filter(CompanyRole.company.has(is_active=True)).all()
    
    eligible_count = 0
    almost_eligible_count = 0
    missing_skills_freq = {}

    for r in roles:
        # Run eligibility engine
        evaluation = evaluate_eligibility(
            profile=profile,
            active_resume=resume,
            rule=r.eligibility_rule,
            skill_weights=r.skill_weights,
            db=db,
        )
        if evaluation["is_eligible"]:
            eligible_count += 1
        elif evaluation["overall_score"] >= 70:
            almost_eligible_count += 1

        for m_skill in evaluation.get("missing_skills", []):
            sname = m_skill["skill_name"]
            missing_skills_freq[sname] = missing_skills_freq.get(sname, 0) + 1

    total_roles = len(roles)
    readiness = int((eligible_count / total_roles) * 100) if total_roles > 0 else 0

    # 2. Study Streak & Hours studied
    sessions = (
        db.query(StudySession)
        .filter(StudySession.user_id == current_user.id)
        .order_by(StudySession.session_date.asc())
        .all()
    )

    total_minutes = sum(s.duration_minutes for s in sessions)
    total_hours = round(total_minutes / 60, 1)

    # Calculate streak (consecutive days)
    streak = 0
    if sessions:
        dates = sorted(list(set([s.session_date.date() for s in sessions])))
        today = datetime.now(timezone.utc).date()
        
        # Check if candidate studied today or yesterday to continue streak
        if dates[-1] == today or dates[-1] == today - timedelta(days=1):
            streak = 1
            for idx in range(len(dates) - 2, -1, -1):
                if dates[idx + 1] - dates[idx] == timedelta(days=1):
                    streak += 1
                else:
                    break
        else:
            streak = 0

    # 3. Tasks statistics
    tasks = db.query(RoadmapTask).filter(RoadmapTask.user_id == current_user.id).all()
    tasks_completed = sum(1 for t in tasks if t.status == "Completed")
    tasks_total = len(tasks)

    # Sort missing skills by frequency
    sorted_missing = [k for k, v in sorted(missing_skills_freq.items(), key=lambda item: item[1], reverse=True)]

    # Recommend next action
    next_action = "Upload resume to initialize learning roadmap."
    if tasks:
        pending_tasks = sorted([t for t in tasks if t.status != "Completed"], key=lambda x: x.priority, reverse=True)
        if pending_tasks:
            next_action = f"Complete task: '{pending_tasks[0].title}' to acquire {pending_tasks[0].skill_name}."
        else:
            next_action = "All roadmap tasks completed! Re-run analyzer or review new target roles."
    elif profile and resume:
        next_action = "Go to Company Hub and trigger eligibility for target roles to seed study tasks."

    # Seed placement readiness trends (simulated visual dates)
    readiness_trend = {
        "Month 1": max(readiness - 20, 20),
        "Month 2": max(readiness - 8, 35),
        "Month 3": readiness
    }

    return {
        "placement_readiness_percentage": readiness,
        "resume_ats_score": resume.analysis.ats_score if resume and resume.analysis else 0,
        "study_streak_days": streak,
        "total_study_hours": total_hours,
        "roadmap_tasks_completed": tasks_completed,
        "roadmap_tasks_total": tasks_total,
        "top_missing_skills": sorted_missing[:5],
        "eligible_companies_count": eligible_count,
        "almost_eligible_companies_count": almost_eligible_count,
        "recommended_next_action": next_action,
        "readiness_trend": readiness_trend
    }


@router.get("/skills", response_model=List[UserSkillProgressResponse])
def get_user_skills(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Retrieve student's technical skill progress list.
    """
    return db.query(UserSkillProgress).filter(UserSkillProgress.user_id == current_user.id).all()


@router.get("/interviews/history", response_model=List[InterviewFeedbackResponse])
def get_interview_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Retrieve student's mock interview feedback history.
    """
    return db.query(InterviewFeedback).filter(InterviewFeedback.user_id == current_user.id).order_by(InterviewFeedback.created_at.desc()).all()
