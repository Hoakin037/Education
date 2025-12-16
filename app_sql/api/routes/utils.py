from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends
from app_sql.core import SECRET_KEY, ALGORITHM, User, get_db
from app_sql.crud import CRUD
import jwt
from jwt import PyJWTError  
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

crud = CRUD()

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error, scheme_name="JWT", description="Вставьте сюда только JWT-токен (без Bearer)")

oauth2_scheme = JWTBearer(auto_error=False)

async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(oauth2_scheme)]
):
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

    user = await crud.get_user(username, db)  # Добавьте await!
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден!")
    return user

async def get_current_active_user(
    user: Annotated[User, Depends(get_current_user)]
):
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user