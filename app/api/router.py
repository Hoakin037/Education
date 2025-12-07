from fastapi import APIRouter
from .routes import auth, item

api_router = APIRouter()
api_router.include_router(auth)
api_router.include_router(item)