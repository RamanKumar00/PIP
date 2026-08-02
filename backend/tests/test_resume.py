import uuid
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.resume import Resume, ResumeAnalysis


# Predefined sample resume text to mock PDF extraction
MOCK_RESUME_TEXT = """
JOHN DOE
john.doe@example.com | +91 9876543210 | Bangalore, India

EDUCATION
State Engineering College - B.Tech in Computer Science
Current CGPA: 8.75/10.00 | Year of Graduation: 2024

SKILLS
Programming: Python, Java, SQL, JavaScript
Backend: FastAPI, Django, REST APIs, Celery
Frontend: React, HTML, CSS, Tailwind CSS
Database: PostgreSQL, Redis
Tools: Docker, Git, GitHub
Cloud: AWS, Heroku

EXPERIENCE
Software Developer Intern at Tech Solutions (Jan 2023 - Present)
- Developed and deployed REST API endpoints using FastAPI and PostgreSQL.
- Worked on login module using JWT token authentication.
- Automated document extraction routines using PyMuPDF.

PROJECTS
E-commerce Platform Project
- Developed E-commerce Website using Django and React.
- Created database schemas for inventory management.
- Worked on login screen and session state management.

CERTIFICATIONS
AWS Certified Solutions Architect Associate (2022)
"""


def get_auth_headers(client: TestClient, email: str) -> dict:
    """Helper to register and login a user, returning Authorization headers.
    """
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


@patch("app.services.resume.report_generator.extract_text_from_pdf")
def test_resume_upload_and_analysis(mock_extract, client: TestClient, db: Session) -> None:
    # 1. Setup mock return value for PDF text parser
    mock_extract.return_value = MOCK_RESUME_TEXT

    headers = get_auth_headers(client, "resumetest@example.com")

    # Mock file upload payload (must be PDF bytes)
    mock_file = ("resume.pdf", b"%PDF-1.4 mock content...", "application/pdf")
    
    # Disable background async task by mocking celery task.delay to call immediately or run synchronously
    with patch("app.api.api_v1.endpoints.resume.analyze_resume_task.delay") as mock_delay:
        # 2. Upload resume
        response = client.post(
            "/api/v1/resume/upload",
            files={"file": mock_file},
            data={"target_role": "Backend Developer"},
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["original_filename"] == "resume.pdf"
        assert data["version"] == 1
        assert data["is_active"] is True
        
        resume_id = data["id"]
        # Check task was dispatched
        mock_delay.assert_called_once_with(resume_id, "Backend Developer")

    # 3. Simulate background worker execution manually (since Celery is mocked)
    from app.worker.tasks import analyze_resume_task
    # Run the worker task synchronously
    success = analyze_resume_task(resume_id, "Backend Developer")
    assert success is True

    # 4. Check status polling endpoint
    status_response = client.get(f"/api/v1/resume/{resume_id}/status", headers=headers)
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["status"] == "completed"
    assert status_data["ats_score"] > 50  # Must calculate a valid score

    # 5. Fetch latest analysis report
    latest_response = client.get("/api/v1/resume/latest", headers=headers)
    assert latest_response.status_code == 200
    latest_data = latest_response.json()
    assert latest_data["id"] == resume_id
    
    analysis = latest_data["analysis"]
    assert analysis["status"] == "completed"
    assert analysis["ats_score"] > 50
    assert len(analysis["suggestions"]) > 0  # Should generate formatting/project suggestions
    
    # Check skills were parsed correctly
    detected_skills = analysis["detected_skills"]
    assert "Python" in detected_skills["programming"]
    assert "FastAPI" in detected_skills["backend"]
    assert "PostgreSQL" in detected_skills["database"]
    
    # Check project analyses
    project_analyses = analysis["project_analyses"]
    assert len(project_analyses) > 0
    assert any("E-commerce" in p["title"] for p in project_analyses)
