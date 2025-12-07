from fastapi import APIRouter, Depends
from app.model import UserBase
from app.auth import get_current_active_user

item = APIRouter(prefix='/users')

@item.get("/users/me", response_model=UserBase)
async def read_users_me(current_user: UserBase = Depends(get_current_active_user)):
    return current_user

@item.get("/users/me/items/")
async def read_own_items(current_user: UserBase = Depends(get_current_active_user)):
    return [{"item_id": "Coffee", "owner": current_user.username}]
