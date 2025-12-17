from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from app_sql.crud import CRUD, get_crud_service
from app_sql.service import AuthService, get_auth_service
from .models import UserUpdateInfo, UserBase
from .utils import  get_current_active_user
from app_sql.core import User, get_db

user = APIRouter(prefix="/user")

@user.get('/get_user_info')
async def get_user_info(
    user: UserBase, 
    current_user: User = Depends(get_current_active_user)):
    if current_user.email != user.email:
        raise HTTPException(status_code=401, detail="Пользователя с таким email нет!")
    return JSONResponse(status_code=200, content={
        "email": current_user.email,
        "name": current_user.name,
        "fullname": current_user.fullname,
    })
        
@user.post('/update_user_info')
async def update_user_info(
    user_data: UserUpdateInfo,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    crud: CRUD = Depends(get_crud_service),
    auth_service: AuthService = Depends(get_auth_service)):
    
    if current_user.email != user_data.email:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    await crud.update_user_info(user_data, db)
    if user_data.new_email is not None:
        tokens = await auth_service.create_tokens_for_user(user_data.new_email, db)
        await crud.update_refresh_token(user_data.new_email, tokens['refresh_token'], db)
        response = JSONResponse(
        content={"detail": "Данные обновлены", "access_token": tokens["access_token"], "token_type": "bearer"}, 
        status_code=200
        )
        response.set_cookie(
            key="refresh_token", 
            value=tokens["refresh_token"], 
            httponly=True, 
            secure=True
        )
        return response
    
    response = JSONResponse(content={"detail": "Данные обновлены"}, status_code=200)
    return response
    
@user.delete("/delete_user")
async def del_user(
    user: UserBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    crud: CRUD = Depends(get_crud_service)):
        if current_user.email != user.email:
            raise HTTPException(status_code=401, detail="Пользователя с таким email нет!")
        await crud.delete_user(user.email, db)
        
        return Response(status_code=204)