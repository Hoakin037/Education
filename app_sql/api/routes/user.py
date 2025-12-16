from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from app_sql.crud import CRUD, get_db
from .models import UserUpdateInfo, UserBase
from .utils import  get_current_active_user
from app_sql.core import User

user = APIRouter(prefix="/user")
crud = CRUD()

@user.get('/get_user_info')
async def get_user_info(
    user: UserBase, 
    current_user: User = Depends(get_current_active_user)):
    try:
        if current_user.email != user.email:
            raise HTTPException(status_code=401, detail="Пользователя с таким email нет!")
        return JSONResponse(status_code=200, content={
            "email": current_user.email,
            "name": current_user.name,
            "fullname": current_user.fullname,
        })
        
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка сервера!")

@user.post('/update_user_info')
async def update_user_info(
    data: UserUpdateInfo,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        if current_user.email != data.current_email:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        data_dict = data.model_dump(exclude_none=True)
        
        await crud.update_user_info(data_dict, db)
        response = JSONResponse(content={"detail": "Данные обновлены"}, status_code=200)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:  
        raise HTTPException(status_code=500, detail="Ошибка сервера!")
    
@user.delete("/delete_user")
async def del_user(
    user: UserBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        if current_user.email != user.email:
            raise HTTPException(status_code=401, detail="Пользователя с таким email нет!")
        crud.delete_user(user.email, db)
        
        return Response(status_code=204)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка сервера!")