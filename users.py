# project/app/api/endpoints/users.py
from fastapi import APIRouter, Depends
from app.schemas.user import User
from app.api import dependencies

users_router = APIRouter()


@users_router.get("/me/", response_model=User)
async def read_users_me(current_user: User = Depends(dependencies.get_current_user)):
    return current_user
