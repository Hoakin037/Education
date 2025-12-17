from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager
from .api.routes import api
from .core import init_db
from fastapi.responses import JSONResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()    
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(api)

@app.exception_handler(Exception) 
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Ошибка сервера!"}
    )

@app.exception_handler(HTTPException)
async def global_httpexception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )