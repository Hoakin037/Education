from core import User, get_db
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, HTTPException
password_hash = PasswordHash.recommended()

async def get_user(email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalars().first()
    if existing_user:
        return existing_user
    return None

async def add_user(data: dict, db: AsyncSession = Depends(get_db)):
    email = data["email"]
    name = data.get("name")   
    fullname = data.get("fullname")
    password = data["password"]

    user = User(email=email, name=name, fullname=fullname, password=password_hash.hash(password), is_active = True)

    existing_user = await get_user(user.email)
    if existing_user != None:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует!")

    db.add(user)
    await db.commit()
    await db.refresh(user)



