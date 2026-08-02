import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.company import Company, CompanyRole, EligibilityRule, CompanySkillWeight
from app.models.profile import Profile
from app.models.user import User
from app.models.resume import Resume, ResumeAnalysis


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


def test_eligibility_engine_logic(client: TestClient, db: Session) -> None:
    # 1. Setup Admin headers
    headers = get_auth_headers(client, "admineligibility@example.com")
    
    # Update user role to admin
    user = db.query(User).filter(User.email == "admineligibility@example.com").first()
    user.role = "admin"
    db.commit()

    # 2. Create Company and Role via REST API
    company_payload = {
        "name": "Tesla",
        "website_url": "https://tesla.com",
        "careers_url": "https://tesla.com/careers",
        "industry": "Automotive / Energy",
        "hq_location": "Austin, TX",
        "hiring_frequency": "Yearly",
        "internship_ppo_available": True,
        "remote_onsite": "Onsite"
    }
    comp_res = client.post("/api/v1/companies/", json=company_payload, headers=headers)
    assert comp_res.status_code == 201
    company_id = comp_res.json()["id"]

    role_payload = {
        "title": "Firmware Engineer",
        "ctc": 22.0,
        "description": "Develop low-level C/C++ control systems firmware.",
        "application_link": "https://tesla.com/careers",
        "difficulty": "Hard",
        "selection_rounds": 3,
        "technical_interview_topics": ["C++", "RTOS", "Microcontrollers"],
        "hr_interview_topics": ["Behavioral", "Teamwork"],
        "eligibility_rule": {
            "min_cgpa": 8.0,
            "allowed_branches": ["CSE", "ECE"],
            "max_active_backlogs": 0,
            "min_resume_match_score": 70
        },
        "skill_weights": [
            {"skill_name": "C++", "importance": 5, "required_level": "Expert"},
            {"skill_name": "Docker", "importance": 3, "required_level": "Beginner"}
        ]
    }
    role_res = client.post(f"/api/v1/companies/{company_id}/roles", json=role_payload, headers=headers)
    assert role_res.status_code == 201
    role_data = role_res.json()
    role_id = role_data["id"]

    # 3. Create Student and Profile (Non-eligible at first)
    headers_student = get_auth_headers(client, "studenteligibility@example.com")
    student = db.query(User).filter(User.email == "studenteligibility@example.com").first()
    
    profile = Profile(
        user_id=student.id,
        full_name="Eligible Student",
        college="Tesla Academy",
        university="State University",
        current_year=4,
        tenth_percentage=92.00,
        twelfth_percentage=90.00,
        phone="9876543210",
        cgpa=7.5,               # Fail: requires >= 8.0
        branch="Mechanical",    # Fail: requires CSE/ECE
        backlogs=0
    )
    db.add(profile)
    db.commit()

    # 4. Check eligibility via API
    check_res = client.get(f"/api/v1/companies/roles/{role_id}/check", headers=headers_student)
    assert check_res.status_code == 200
    check_data = check_res.json()
    assert check_data["is_eligible"] is False
    assert check_data["overall_score"] < 50
    assert len(check_data["reasons"]) >= 3
    reasons_str = " ".join(check_data["reasons"])
    assert "cgpa" in reasons_str.lower()
    assert "branch" in reasons_str.lower()
    assert any("Missing critical skill: C++" in r for r in check_data["reasons"])
    
    # 5. Update profile to meet academic criteria
    profile.cgpa = 8.5
    profile.branch = "CSE"
    db.commit()
    
    # Create active resume containing target skills (C++ and Docker)
    resume = Resume(
        user_id=student.id,
        original_filename="res.pdf",
        stored_filename="res.pdf",
        file_size=100,
        mime_type="application/pdf",
        version=1,
        is_active=True
    )
    db.add(resume)
    db.commit()
    
    analysis = ResumeAnalysis(
        resume_id=resume.id,
        status="completed",
        ats_score=80,
        detected_skills={
            "programming": ["C++"],
            "backend": [],
            "frontend": [],
            "database": ["Docker"],
            "tools": [],
            "cloud": []
        },
        detailed_breakdown={
            "formatting_score": 20,
            "grammar_score": 20,
            "keyword_score": 20,
            "project_score": 20,
            "experience_score": 10,
            "achievements_score": 10,
            "strength_meter": {
                "quality_label": "Excellent",
                "stars": 5,
                "readability": 100,
                "professionalism": 100,
                "technical_strength": 100,
                "ats_compatibility": 100
            },
            "role_match": {
                "role_name": "Firmware Engineer",
                "match_percentage": 100,
                "matched_skills": ["C++", "Docker"],
                "missing_skills": []
            }
        }
    )
    db.add(analysis)
    db.commit()

    # 6. Re-evaluate eligibility (should now be eligible)
    check_res_2 = client.get(f"/api/v1/companies/roles/{role_id}/check", headers=headers_student)
    assert check_res_2.status_code == 200
    check_data_2 = check_res_2.json()
    assert check_data_2["is_eligible"] is True
    assert check_data_2["overall_score"] == 100
    assert len(check_data_2["reasons"]) == 0
    assert check_data_2["estimated_effort"] == "0 weeks"
