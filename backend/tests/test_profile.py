from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


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


def test_get_profile_not_found(client: TestClient) -> None:
    headers = get_auth_headers(client, "noprofile@example.com")
    response = client.get("/api/v1/profile/", headers=headers)
    assert response.status_code == 404
    assert "Profile not found" in response.json()["detail"]


def test_upsert_profile_success(client: TestClient) -> None:
    headers = get_auth_headers(client, "profile_success@example.com")
    profile_payload = {
        "full_name": "John Doe",
        "college": "State Engineering College",
        "university": "State University",
        "branch": "Computer Science & Engineering",
        "current_year": 3,
        "cgpa": 8.75,
        "tenth_percentage": 92.5,
        "twelfth_percentage": 88.0,
        "phone": "9876543210",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "github_url": "https://github.com/johndoe",
        "portfolio_url": "https://johndoe.dev",
        "preferred_role": "Software Engineer",
        "preferred_companies": ["Amazon", "TCS"],
        "backlogs": 0,
    }
    
    # Save (create) profile
    response = client.put("/api/v1/profile/", json=profile_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "John Doe"
    assert float(data["cgpa"]) == 8.75
    assert data["backlogs"] == 0

    # Get profile
    get_response = client.get("/api/v1/profile/", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["college"] == "State Engineering College"


def test_update_profile_validation_error(client: TestClient) -> None:
    headers = get_auth_headers(client, "profile_fail@example.com")
    # CGPA above 10.0 should fail
    bad_payload = {
        "full_name": "John Doe",
        "college": "State Engineering College",
        "university": "State University",
        "branch": "Computer Science & Engineering",
        "current_year": 3,
        "cgpa": 12.5,  # Invalid CGPA
        "tenth_percentage": 92.5,
        "twelfth_percentage": 88.0,
        "phone": "9876543210",
        "backlogs": 0,
    }
    response = client.put("/api/v1/profile/", json=bad_payload, headers=headers)
    assert response.status_code == 422  # Pydantic validation error
