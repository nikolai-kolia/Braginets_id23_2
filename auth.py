# project/app/api/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session, get_db
from app.schemas.user import UserCreate, User, Token, UserLogin
from app.cruds import user as user_crud
from app.core import security
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

auth_router = APIRouter()

@auth_router.post("/sign-up/", response_model=User)
def sign_up(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = user_crud.create_user(db, user)
    access_token_expires = timedelta(minutes=30)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    db_user.token = access_token
    return db_user


@auth_router.post("/login/", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = user_crud.get_user_by_email(db, form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=30)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}