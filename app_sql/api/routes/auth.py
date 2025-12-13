from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from fastapi import APIRouter
from jwt import PyJWTError  
from sqlalchemy.ext.asyncio import AsyncSession

from .jwt import create_token
from app_sql.crud import CRUD, get_db
from .models import UserRegister, UpdatePassword, UserUpdateInfo
from .utils import oauth2_scheme
from app_sql.core import SECRET_KEY, ALGORITHM, password_hash

auth = APIRouter(prefix="/auth")
crud = CRUD()


@auth.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(user: UserRegister, db: AsyncSession = Depends(get_db)):
    try:
        await crud.add_user({
            "email": user.email,
            'name': user.name,
            'fullname': user.fullname,
            'password': password_hash.hash(user.password),
            'is_active': False
        }, db)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка сервера!")
    return {
        "name": user.name,
        "email": user.email,
        "fullname": user.fullname,
        "is_active": False  
    }

@auth.post('/login')
async def login(credentials: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_db)):
    try:
        user = await crud.get_user(credentials.username, db)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if not password_hash.verify(credentials.password, user.password):
            print(f"Email: {user.email}, Password Match: False") 
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        refresh_token = create_token({"sub": credentials.username}, 'refresh')
        access_token = create_token({"sub": credentials.username}, 'access')

        await crud.update_refresh_token(credentials.username, refresh_token, db)

        response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"}, status_code=200)
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True)
        return response
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e
    
    

@auth.post('/refresh_tokens')
async def refresh_tokens(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    token = credentials.credentials  

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        if not email or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Неверный refresh token")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Неверный или просроченный refresh token")

    user = await crud.get_user(email, db)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    access_token=create_token({"sub": email}, "access")
    refresh_token=create_token({"sub": email}, 'refresh')
    
    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True) # Добавляем RT в куки
    return response