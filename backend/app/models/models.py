'''
This file contains the SQLAlchemy models for the application.
'''

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)

    documents = relationship("Document", back_populates="owner")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="documents")
    jobs = relationship("ProcessingJob", back_populates="document")

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}')>"


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    content = Column(Text)

    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}')>"


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    status = Column(String)
    result = Column(Text)

    document = relationship("Document", back_populates="jobs")

    def __repr__(self):
        return f"<ProcessingJob(id={self.id}, status='{self.status}')>"


class LegalReference(Base):
    __tablename__ = "legal_references"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    source = Column(String)

    def __repr__(self):
        return f"<LegalReference(id={self.id})>"
