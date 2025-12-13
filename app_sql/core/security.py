from dotenv import dotenv_values
from pwdlib import PasswordHash
from pathlib import Path

current_dir = Path(__file__).parent
env_path = current_dir / ".env"

config = dotenv_values(str(env_path))

SECRET_KEY = config.get("SECRET_KEY")
ALGORITHM = config.get("ALGORITHM")

password_hash = PasswordHash.recommended()

if not SECRET_KEY:
    raise EnvironmentError("Переменная окружения 'SECRET_KEY' не найдена. Проверьте .env файл.")