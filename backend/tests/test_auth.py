import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api.deps import get_db
from app.db.database import Base

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)


def test_register():
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

def test_test_token():
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