from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from fastapi import APIRouter
from jwt import PyJWTError  
from sqlalchemy.ext.asyncio import AsyncSession

from app_sql.crud import get_crud_service, CRUD
from app_sql.service import AuthService, get_auth_service
from .models import UserRegister, UpdatePassword
from .utils import oauth2_scheme, get_current_active_user
from app_sql.core import SECRET_KEY, ALGORITHM, password_hash, User, get_db

auth = APIRouter(prefix="/auth")

@auth.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(user: UserRegister, 
                 db: AsyncSession = Depends(get_db),
                 auth_service: AuthService = Depends(get_auth_service)):
    await auth_service.register_new_user(user, db)
    return {
        "name": user.name,
        "email": user.email,
        "fullname": user.fullname,
        "is_active": False  
    }

@auth.post('/login')
async def login(credentials: Annotated[OAuth2PasswordRequestForm, Depends()], 
                db: AsyncSession = Depends(get_db),
                auth_service: AuthService = Depends(get_auth_service)):
    user = await auth_service.authenticate_user(credentials.username, credentials.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    tokens = await auth_service.create_tokens_for_user(user.email, db)

    response = JSONResponse(
        content={"access_token": tokens["access_token"], "token_type": "bearer"}, 
        status_code=200
    )
    response.set_cookie(
        key="refresh_token", 
        value=tokens["refresh_token"], 
        httponly=True, 
        secure=True
    )
    return response
        

@auth.post('/refresh_tokens')
async def refresh_tokens(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme), 
                         db: AsyncSession = Depends(get_db),
                         crud: CRUD = Depends(get_crud_service),
                         auth_service: AuthService = Depends(get_auth_service)):
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

    tokens = await auth_service.create_tokens_for_user(user.email, db)
    
    await crud.update_refresh_token(email, tokens["refresh_token"], db)

    response = JSONResponse(
        content={"access_token": tokens["access_token"], "token_type": "bearer"}, 
        status_code=200
    )
    response.set_cookie(
        key="refresh_token", 
        value=tokens["refresh_token"], 
        httponly=True, 
        secure=True
    )
    return response

@auth.post('/update_password')
async def update_password(credentials: UpdatePassword, 
                          db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_active_user),
                          crud: CRUD = Depends(get_crud_service)):
    if current_user.email != credentials.email:
        raise HTTPException(status_code=403, detail="Пользователя с таким email не сущетсвует!")
    
    if password_hash.verify(credentials.current_password, current_user.password):
        
        await crud.update_user_password({
            "email": credentials.email,
            "password": password_hash.hash(credentials.new_password)},
            db)
        return JSONResponse(status_code=200, content={
            "detail": "Пароль успешно изменен!"
        })
    else:
        raise HTTPException(status_code=401, detail="Неверный пароль!")
    