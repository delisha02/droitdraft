import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.api.deps import get_db
from app.db.database import Base
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.crud import document as crud_document
from app.crud import user as crud_user
from app.schemas.user import UserCreate

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)
    yield db
    db.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c


def test_create_document(db):
    user_in = UserCreate(email="test@example.com", password="password", full_name="Test User")
    user = crud_user.user.create(db, obj_in=user_in)
    document_in = DocumentCreate(title="Test Document", content="Test content", owner_id=user.id)
    document = crud_document.document.create(db, obj_in=document_in)
    assert document.title == "Test Document"
    assert document.content == "Test content"
    assert document.owner_id == user.id


def test_get_document(db):
    user_in = UserCreate(email="test@example.com", password="password", full_name="Test User")
    user = crud_user.user.create(db, obj_in=user_in)
    document_in = DocumentCreate(title="Test Document", content="Test content", owner_id=user.id)
    document = crud_document.document.create(db, obj_in=document_in)
    retrieved_document = crud_document.document.get(db, id=document.id)
    assert retrieved_document
    assert retrieved_document.id == document.id
    assert retrieved_document.title == document.title


def test_update_document(db):
    user_in = UserCreate(email="test@example.com", password="password", full_name="Test User")
    user = crud_user.user.create(db, obj_in=user_in)
    document_in = DocumentCreate(title="Test Document", content="Test content", owner_id=user.id)
    document = crud_document.document.create(db, obj_in=document_in)
    document_update = DocumentUpdate(title="Updated Document")
    updated_document = crud_document.document.update(db, db_obj=document, obj_in=document_update)
    assert updated_document.title == "Updated Document"


def test_delete_document(db):
    user_in = UserCreate(email="test@example.com", password="password", full_name="Test User")
    user = crud_user.user.create(db, obj_in=user_in)
    document_in = DocumentCreate(title="Test Document", content="Test content", owner_id=user.id)
    document = crud_document.document.create(db, obj_in=document_in)
    deleted_document = crud_document.document.remove(db, id=document.id)
    assert deleted_document.id == document.id
    retrieved_document = crud_document.document.get(db, id=document.id)
    assert retrieved_document is None
