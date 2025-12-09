from os import getenv
from dotenv import load_dotenv
from jwt import PyJWTError  
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException
from .db import get_user
from .model import ValidationError, UserBase


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error, scheme_name="JWT", description="Вставьте сюда только JWT-токен (без Bearer)")

oauth2_scheme = JWTBearer(auto_error=False)


load_dotenv()
SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")
password_hash = PasswordHash.recommended()

def create_token(data: dict, token_type: str, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({'exp': expire, "type": token_type})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not password_hash.verify(password, user.hashed_password):
        raise ValidationError("Неверный логин или пароль!")
    return user

async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(oauth2_scheme)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    
    token = credentials.credentials  
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Неверный токен")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Токен просрочен или повреждён")

    user = get_user(username)
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден!")
    return user

async def get_current_active_user(current_user: UserBase = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user