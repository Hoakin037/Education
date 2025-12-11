from fastapi import Depends, HTTPException
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not password_hash.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль!")
    return user