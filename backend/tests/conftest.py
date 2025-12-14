import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app as fastapi_app  # Rename the import
from app.api.deps import get_db
from app.db.database import Base
import app.models.models


SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.drop_all(bind=engine) # Drop existing tables for a clean slate
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    """
    Pytest fixture to provide a database session for each test function.
    This fixture creates a new session for each test, and rolls back any
    changes made during the test to ensure test isolation.
    """
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()

@pytest.fixture(scope="function")
def client(db):
    """
    Pytest fixture to provide a TestClient with an overridden database session.
    This client will use the isolated database session provided by the `db` fixture.
    """
    fastapi_app.dependency_overrides[get_db] = lambda: db  # Use the renamed import
    with TestClient(fastapi_app) as c:  # Use the renamed import
        yield c