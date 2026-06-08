from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_user_can_register_login_and_read_profile():
    email = f"user-{uuid4().hex}@example.com"

    with TestClient(app) as client:
        register_response = client.post(
            "/auth/register",
            json={
                "email": email,
                "full_name": "Test User",
                "password": "strong-password",
            },
        )
        login_response = client.post(
            "/auth/login",
            json={"email": email, "password": "strong-password"},
        )
        token = login_response.json()["access_token"]
        profile_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert register_response.status_code == 201
    assert login_response.status_code == 200
    assert profile_response.status_code == 200
    assert profile_response.json()["email"] == email


def test_profile_requires_authentication():
    with TestClient(app) as client:
        response = client.get("/auth/me")

    assert response.status_code == 401
