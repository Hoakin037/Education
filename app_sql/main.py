from fastapi import FastAPI, Request, HTTPException, status
from contextlib import asynccontextmanager
from .api.routes import api
from .core import init_db
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Ошибка валидации",
            "errors": errors,
        }
    )