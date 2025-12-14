import pytest
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.schemas.user import UserCreate
from app.crud import document as crud_document
from app.crud import user as crud_user


def test_create_document(db):
    user_in = UserCreate(email="test@example.com", password="password", full_name="Test User")
    user = crud_user.create(db, obj_in=user_in)
    document_in = DocumentCreate(title="Test Document", content="Test content", owner_id=user.id)
    document = crud_document.create(db, obj_in=document_in)
    assert document.title == "Test Document"
    assert document.content == "Test content"
    assert document.owner_id == user.id


def test_get_document(db):
    user_in = UserCreate(email="test@example.com", password="password", full_name="Test User")
    user = crud_user.create(db, obj_in=user_in)
    document_in = DocumentCreate(title="Test Document", content="Test content", owner_id=user.id)
    document = crud_document.create(db, obj_in=document_in)
    retrieved_document = crud_document.get(db, id=document.id)
    assert retrieved_document
    assert retrieved_document.id == document.id
    assert retrieved_document.title == document.title


def test_update_document(db):
    user_in = UserCreate(email="test@example.com", password="password", full_name="Test User")
    user = crud_user.create(db, obj_in=user_in)
    document_in = DocumentCreate(title="Test Document", content="Test content", owner_id=user.id)
    document = crud_document.create(db, obj_in=document_in)
    document_update = DocumentUpdate(title="Updated Document")
    updated_document = crud_document.update(db, db_obj=document, obj_in=document_update)
    assert updated_document.title == "Updated Document"


def test_delete_document(db):
    user_in = UserCreate(email="test@example.com", password="password", full_name="Test User")
    user = crud_user.create(db, obj_in=user_in)
    document_in = DocumentCreate(title="Test Document", content="Test content", owner_id=user.id)
    document = crud_document.create(db, obj_in=document_in)
    deleted_document = crud_document.remove(db, id=document.id)
    assert deleted_document.id == document.id
    retrieved_document = crud_document.get(db, id=document.id)
    assert retrieved_document is None