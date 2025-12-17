from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends
from app_sql.core import SECRET_KEY, ALGORITHM, User, get_db
from app_sql.crud import CRUD
import jwt
from jwt import PyJWTError  
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

crud = CRUD()


oauth2_scheme = HTTPBearer()

async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(oauth2_scheme)]
):
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