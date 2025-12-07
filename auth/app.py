from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from jwt import PyJWTError  
from pwdlib import PasswordHash
from pydantic import BaseModel, Field


SECRET_KEY = "51c0831c0d2ed110d83a743ef421cf36f701220ed4873ed8ed9602ac02553f76"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60          # 1 час
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 дней


fake_users_db: dict[str, dict] = {}
password_hash = PasswordHash.recommended()


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error, scheme_name="JWT", description="Вставьте сюда только JWT-токен (без Bearer)")

oauth2_scheme = JWTBearer(auto_error=False)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

class SignUp(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str | None = None
    full_name: str | None = None
    password: str = Field(..., min_length=8)

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "username": "alice",
                "email": "alice@example.com",
                "full_name": "Alice Wonder",
                "password": "supersecret123"
            }]
        }
    }

class SignUpResp(BaseModel):
    username: str
    email: str | None
    full_name: str | None
    disabled: bool = False


app = FastAPI(title="Мой крутой API с регистрация + JWT + refresh")


# Утилиты

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user(username: str):
    if username in fake_users_db:
        return UserInDB(**fake_users_db[username])
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not password_hash.verify(password, user.hashed_password):
        return None
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
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Роуты

@app.post("/signup", response_model=SignUpResp, status_code=status.HTTP_201_CREATED)
async def signup(user_in: SignUp):
    if user_in.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    hashed = password_hash.hash(user_in.password)
    fake_users_db[user_in.username] = {
        "username": user_in.username,
        "email": user_in.email,
        "full_name": user_in.full_name,
        "hashed_password": hashed,
        "disabled": False,
    }
    return SignUpResp(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
    )

@app.post("/token", response_model=Token)
async def login_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})

    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True) # Добавляем RT в куки
    return response

@app.post("/token/refresh", response_model=TokenRefresh)
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

    return TokenRefresh(
        access_token=create_access_token({"sub": user.username}),
        refresh_token=create_refresh_token({"sub": user.username})
    )

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Coffee", "owner": current_user.username}]