from sqlalchemy.ext.asyncio import AsyncSession
from app_sql.core import password_hash
from app_sql.crud import CRUD
from app_sql.api.routes.jwt import create_token 

class AuthService:
    def __init__(self):
        self.crud = CRUD()

    async def register_new_user(self, user_data, db: AsyncSession):
        hashed_password = password_hash.hash(user_data.password)
        
        await self.crud.add_user({
            "email": user_data.email,
            "name": user_data.name,
            "fullname": user_data.fullname,
            "password": hashed_password,
            "is_active": False
        }, db)

    async def authenticate_user(self, email: str, password: str, db: AsyncSession):
        user = await self.crud.get_user(email, db)
        if not user:
            return None
        if not password_hash.verify(password, user.password):
            return None
        return user

    async def create_tokens_for_user(self, email: str, db: AsyncSession):
        access_token = create_token({"sub": email}, 'access')
        refresh_token = create_token({"sub": email}, 'refresh')

        await self.crud.update_refresh_token(email, refresh_token, db)

        return {
            "access_token": access_token, 
            "refresh_token": refresh_token
        }
    
def get_auth_service():
    return AuthService()