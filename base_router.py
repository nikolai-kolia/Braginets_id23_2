# project/app/api/base_router.py

from fastapi import APIRouter
from .routers.auth import auth_router
from .routers.users import users_router
from .routers.website_parsing import parsing_router
base_router = APIRouter()

base_router.include_router(auth_router)
base_router.include_router(users_router)
base_router.include_router(parsing_router)