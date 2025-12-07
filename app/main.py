from fastapi import FastAPI, APIRouter
from .api.router import api_router
api = FastAPI()
api.include_router(api_router)