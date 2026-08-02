from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_signup_successful(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": "teststudent@example.com", "password": "SecurePassword123!"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "teststudent@example.com"
    assert "id" in data
    assert data["role"] == "student"


def test_signup_duplicate_email(client: TestClient) -> None:
    # First sign up
    client.post(
        "/api/v1/auth/signup",
        json={"email": "duplicate@example.com", "password": "SecurePassword123!"},
    )
    # Try duplicate signup
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": "duplicate@example.com", "password": "AnotherPassword123!"},
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_successful(client: TestClient) -> None:
    # Signup
    email = "login_success@example.com"
    password = "SecurePassword123!"
    client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": password},
    )
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_login_incorrect_credentials(client: TestClient) -> None:
    # Signup
    email = "wrong_cred@example.com"
    password = "SecurePassword123!"
    client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": password},
    )
    # Wrong password login
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "WrongPassword!"},
    )
    assert response.status_code == 400
    assert "Incorrect email or password" in response.json()["detail"]
