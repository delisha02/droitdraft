'''
This file contains user Pydantic models (base, create, response).
'''

from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel):
    email: EmailStr


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str
    full_name: str | None = None


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: str | None = None
    full_name: str | None = None


class UserInDBBase(UserBase):
    id: int
    full_name: str | None = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
