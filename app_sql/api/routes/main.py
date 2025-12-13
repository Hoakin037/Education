from fastapi import APIRouter
from .auth import auth
from .user import user

api = APIRouter(prefix='/api')

api.include_router(auth)
api.include_router(user)
