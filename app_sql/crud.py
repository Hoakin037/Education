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
    user = User(email=email, name=name, fullname=fullname, password=password_hash.hash(password))

    existing_user = await get_user(user.email)
    if existing_user != None:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует!")

    db.add(user)
    await db.commit()
    await db.refresh(user)

async def update_user_info(data: dict, db: AsyncSession = Depends(get_db)):
    current_email = data['current_email']
    new_email = data['new_email']
    name = data['name']
    fullname = data['fullname']

    existing_user = await get_user(current_email)
    if existing_user != None:
        existing_user.email = new_email if new_email else current_email
        existing_user.name =  name if name else existing_user.name
        existing_user.fullname = fullname if fullname else existing_user.fullname

        await db.commit()
    else:
        raise HTTPException(status_code=404, detail="Пользователь не найден!")


async def update_user_password(data: dict, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user(data['email'])
    if existing_user != None:
        if password_hash.verify(data['password'], existing_user.password):
            existing_user.password = password_hash.hash(data['password'])
            await db.commit()
        else:
            raise HTTPException(status_code=401, detail="Неверный пароль!")
    else:
        raise HTTPException(status_code=404, detail="Пользователь не найден!")

async def delete_user(email: str, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user(email)
    if existing_user != None:
        db.delete(existing_user)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Пользователь не найден!")
    
    
