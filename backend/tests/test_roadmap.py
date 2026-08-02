import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.company import Company, CompanyRole, EligibilityRule, CompanySkillWeight
from app.models.profile import Profile
from app.models.user import User
from app.models.roadmap import LearningResource, RoadmapTask, UserSkillProgress, StudySession


def get_auth_headers(client: TestClient, email: str) -> dict:
    client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": "SecurePassword123!"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SecurePassword123!"},
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def test_roadmap_coach_system(client: TestClient, db: Session) -> None:
    # 1. Setup Admin & seed data
    headers_admin = get_auth_headers(client, "adminroadmap@example.com")
    admin = db.query(User).filter(User.email == "adminroadmap@example.com").first()
    admin.role = "admin"
    db.commit()

    # Create Company and SDE Role
    comp = Company(name="Netflix", website_url="https://netflix.com", hiring_frequency="Yearly")
    db.add(comp)
    db.commit()
    db.refresh(comp)

    role = CompanyRole(
        company_id=comp.id,
        title="SDE-1",
        ctc=32.0,
        difficulty="Hard",
        selection_rounds=3
    )
    db.add(role)
    db.commit()
    db.refresh(role)

    rule = EligibilityRule(
        role_id=role.id,
        min_cgpa=8.0,
        allowed_branches=["CSE"],
        max_active_backlogs=0,
        min_resume_match_score=60
    )
    db.add(rule)

    # Require Python (Critical) and Docker (Important)
    db.add(CompanySkillWeight(role_id=role.id, skill_name="Python", importance=5, required_level="Expert"))
    db.add(CompanySkillWeight(role_id=role.id, skill_name="Docker", importance=4, required_level="Intermediate"))
    db.commit()

    # Seed one learning resource for Docker
    res = LearningResource(
        skill_name="Docker",
        title="Docker Container Fundamentals",
        url="https://youtube.com",
        estimated_hours=6,
        difficulty="Intermediate"
    )
    db.add(res)
    db.commit()

    # 2. Setup Student & Profile (Missing Python and Docker)
    headers_student = get_auth_headers(client, "studentroadmap@example.com")
    student = db.query(User).filter(User.email == "studentroadmap@example.com").first()
    
    profile = Profile(
        user_id=student.id,
        full_name="Roadmap Student",
        college="Netflix Academy",
        university="State University",
        current_year=4,
        tenth_percentage=90.0,
        twelfth_percentage=90.0,
        phone="9876543211",
        cgpa=8.5,
        branch="CSE",
        backlogs=0
    )
    db.add(profile)
    db.commit()

    # 3. Generate Roadmap tasks from skill gaps
    gen_res = client.post(f"/api/v1/roadmap/generate/{role.id}", headers=headers_student)
    assert gen_res.status_code == 200
    tasks_list = gen_res.json()
    assert len(tasks_list) >= 2  # Tasks for Python and Docker

    # Verify task attributes
    docker_task = [t for t in tasks_list if "Docker" in t["skill_name"]][0]
    assert docker_task["status"] == "Not Started"
    assert docker_task["priority"] == 4
    
    # 4. Check initial UserSkillProgress is created
    prog = db.query(UserSkillProgress).filter(
        UserSkillProgress.user_id == student.id,
        UserSkillProgress.skill_name.ilike("Docker")
    ).first()
    assert prog is not None
    assert prog.confidence_score == 0
    assert prog.mastery_level == "Beginner"

    # 5. Log a Study Session
    session_payload = {
        "duration_minutes": 120,
        "focus_score": 5,
        "energy_level=4": 4,
        "resource_used": "YouTube Docker",
        "notes": "Learned dockerfiles and caching layers."
    }
    # Slight fix: FastAPI Pydantic parses fields without energy_level=4. We pass standard payload:
    session_payload = {
        "duration_minutes": 120,
        "focus_score": 5,
        "energy_level": 4,
        "resource_used": "YouTube Docker",
        "notes": "Learned dockerfiles."
    }
    session_res = client.post(
        f"/api/v1/roadmap/tasks/{docker_task['id']}/study-sessions",
        json=session_payload,
        headers=headers_student
    )
    assert session_res.status_code == 200
    
    # Assert task progress updated
    task_res = client.get("/api/v1/roadmap/tasks", headers=headers_student)
    assert task_res.status_code == 200
    updated_docker = [t for t in task_res.json() if t["id"] == docker_task["id"]][0]
    assert updated_docker["status"] == "In Progress"
    assert updated_docker["progress_percentage"] > 0

    # 6. Complete study task and trigger closed loop proficiency boost
    complete_res = client.put(
        f"/api/v1/roadmap/tasks/{docker_task['id']}/status?status_str=Completed",
        headers=headers_student
    )
    assert complete_res.status_code == 200
    
    # Assert UserSkillProgress confidence boosted
    db.expire_all()
    prog_updated = db.query(UserSkillProgress).filter(
        UserSkillProgress.user_id == student.id,
        UserSkillProgress.skill_name.ilike("Docker")
    ).first()
    assert prog_updated.confidence_score == 30  # Increased by 30

    # 7. Check Dashboard analytics endpoint
    dash_res = client.get("/api/v1/roadmap/dashboard-analytics", headers=headers_student)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["study_streak_days"] == 1
    assert dash_data["total_study_hours"] == 2.0  # 120 mins = 2 hours
    assert dash_data["roadmap_tasks_completed"] == 1
