from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from fastapi import APIRouter
from jwt import PyJWTError  

from api.model import SignUpResp, SignUp, Token
from api.db import get_user, add_user
from api.auth import password_hash, authenticate_user, create_token, oauth2_scheme, SECRET_KEY, ALGORITHM

auth = APIRouter()

@auth.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user_in: SignUp):
    if get_user(user_in.username) != None:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    hashed = password_hash.hash(user_in.password)
    add_user(user_in.username, {
        "username": user_in.username,
        "email": user_in.email,
        "full_name": user_in.full_name,
        "hashed_password": hashed,
        "disabled": False,
    })

    return {
        "username": user_in.username,
        "email": user_in.email,
        "full_name": user_in.full_name,
        "disabled": False  
    }

@auth.post("/token", response_model=Token)
async def login_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_token({"sub": user.username}, "access")
    refresh_token = create_token({"sub": user.username}, "refresh")

    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True) # Добавляем RT в куки
    return response

@auth.post("/token/refresh", response_model=Token)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials 

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        if not username or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Неверный refresh token")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Неверный или просроченный refresh token")

    user = get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    return Token(
        access_token=create_token({"sub": user.username}, "access"),
        refresh_token=create_token({"sub": user.username}, 'refresh')
    )