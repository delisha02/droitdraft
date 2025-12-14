from fastapi.testclient import TestClient
from app.main import app

def test_register(client: TestClient):

    response = client.post(

        "/api/v1/auth/register",

        json={"email": "test@example.com", "password": "test", "full_name": "Test User"},

    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "test@example.com"

    assert "id" in data

    assert "full_name" in data

    assert "hashed_password" not in data



def test_test_token(client: TestClient):

    # Register a new user

    client.post(

        "/api/v1/auth/register",

        json={"email": "test2@example.com", "password": "test", "full_name": "Test User"},

    )



    # Log in to get a token

    login_response = client.post(

        "/api/v1/auth/login/access-token",

        data={"username": "test2@example.com", "password": "test"},

    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]



    # Call test-token endpoint

    response = client.post(

        "/api/v1/auth/login/test-token",

        headers={"Authorization": f"Bearer {token}"},

    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "test2@example.com"
