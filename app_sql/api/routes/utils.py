from pwdlib import PasswordHash
from fastapi.security import HTTPBearer

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error, scheme_name="JWT", description="Вставьте сюда только JWT-токен (без Bearer)")

oauth2_scheme = JWTBearer(auto_error=False)

