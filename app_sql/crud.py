from .core import User, get_db
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, HTTPException

class CRUD():
    
    async def get_user(self, email: str, db: AsyncSession):
        try:
            result = await db.execute(select(User).where(User.email == email))
            existing_user = result.scalars().first()
            if existing_user:
                return existing_user
            return None
        except Exception:
            raise HTTPException(status_code=500, detail="Ошибка обращения к БД!")

    async def add_user(self, data: dict, db: AsyncSession):
        email = data["email"]
        name = data.get("name")   
        fullname = data.get("fullname")
        password = data["password"]
        user = User(email=email, name=name, fullname=fullname, password=password)

        existing_user = await self.get_user(user.email, db)
        if existing_user != None:
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует!")

        db.add(user)
        await db.commit()
        await db.refresh(user)

    async def update_user_info(self, data: dict, db: AsyncSession):
        current_email = data['current_email']  # Обязательное поле, оставляем как есть
        new_email = data.get('new_email')      # Измените на get
        name = data.get('name')                # Измените на get
        fullname = data.get('fullname')        # Измените на get

        existing_user = await self.get_user(current_email, db)
        if existing_user is not None:  # Исправьте на is not None (лучшая практика)
            existing_user.email = new_email if new_email else current_email
            existing_user.name = name if name else existing_user.name
            existing_user.fullname = fullname if fullname else existing_user.fullname

            await db.commit()
        else:
            raise HTTPException(status_code=404, detail="Пользователь не найден!")


    async def update_user_password(self, data: dict, db: AsyncSession):
        existing_user = await self.get_user(data['email'], db)
        if existing_user != None:
                existing_user.password = data['password']
        else:
            raise HTTPException(status_code=404, detail="Пользователь не найден!")

    async def update_refresh_token(self, email: str, new_token: str, db: AsyncSession):
        existing_user = await self.get_user(email, db)
        if existing_user != None:
            existing_user.refresh_token = new_token
            existing_user.is_active = True
            await db.commit() 
        else:
            raise HTTPException(status_code=401, detail="Неверный пароль!")
        
    async def delete_user(self, email: str, db: AsyncSession):
        existing_user = await self.get_user(email, db)
        if existing_user != None:
            await db.delete(existing_user)
            await db.commit()
        else:
            raise HTTPException(status_code=404, detail="Пользователь не найден!")
        
        
