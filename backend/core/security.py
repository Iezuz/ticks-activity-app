import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

from backend.core.constants import TOKEN_EXPIRE_TIME

from backend.core.config import settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_TIME)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        #print("PAYLOAD:", payload)
        print("SECRET_KEY:", type(settings.SECRET_KEY))
        return payload

    except JWTError:
        return None