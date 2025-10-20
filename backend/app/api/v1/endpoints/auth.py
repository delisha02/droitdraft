'''
This file defines authentication routes (register, login, refresh, logout, me).
'''

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.models import models
from app.schemas import user, token
from app.api import deps
from app.core import security
from app.core.config import settings
from app.crud import user as crud_user

router = APIRouter()


@router.post("/login/access-token", response_model=token.Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud_user.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.email, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/login/test-token", response_model=user.User)
def test_token(
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Test access token
    """
    return current_user


@router.post("/register", response_model=user.User)
def register(
    *, 
    db: Session = Depends(deps.get_db), 
    user_in: user.UserCreate
):
    """
    Create new user.
    """
    user = crud_user.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud_user.user.create(db, obj_in=user_in)
    return user
