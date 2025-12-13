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
from .utils import oauth2_scheme, get_current_active_user
from app_sql.core import SECRET_KEY, ALGORITHM, password_hash, User

user = APIRouter(prefix="/user")
crud = CRUD()

@user.post('/update_user_info')
async def update_user_info(
    data: UserUpdateInfo,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Проверка на совпадение email для безопасности
        if current_user.email != data.current_email:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Преобразуем модель в dict, исключаем None
        data_dict = data.model_dump(exclude_none=True)
        
        await crud.update_user_info(data_dict, db)
        response = JSONResponse(content={"detail": "Данные обновлены"}, status_code=200)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:  # Добавьте as e для отладки
        print(e)  # Вывод исключения в консоль сервера для логирования
        raise HTTPException(status_code=500, detail="Ошибка сервера!")