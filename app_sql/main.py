from fastapi import FastAPI
from contextlib import asynccontextmanager
from .api.routes import api
from .core import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()    
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(api)