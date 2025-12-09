from fastapi import FastAPI, APIRouter
from api import api_router

api = FastAPI()
api.include_router(api_router)