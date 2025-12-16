from app_sql.core import SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta, timezone
from jwt import encode

def create_token(data: dict, token_type: str, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({'exp': expire, "type": token_type})
    return encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) 