from fastapi import APIRouter
from .auth import auth

api = APIRouter(prefix='/api')

api.include_router(auth)
