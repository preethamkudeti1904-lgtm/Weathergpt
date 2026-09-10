from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt
import bcrypt
import logging
from app.core.config import settings

logger = logging.getLogger("auth.password")
MAX_BCRYPT_BYTES = 72

class PasswordService:
    @staticmethod
    def get_byte_length(password: str) -> int:
        if not isinstance(password, str):
            raise TypeError("Password must be a string.")
        return len(password.encode("utf-8"))

    @classmethod
    def validate_password(cls, password: str) -> None:
        if not isinstance(password, str) or not password:
            raise ValueError("Password is required.")
        byte_len = cls.get_byte_length(password)
        # Temporary development logging: reports ONLY byte length, never the password or hash
        logger.info(f"[PasswordService] Password UTF-8 byte length: {byte_len}")
        print(f"[PasswordService] Password UTF-8 byte length: {byte_len}")

        if byte_len > MAX_BCRYPT_BYTES:
            raise ValueError("Password is too long. Please use a password of 72 UTF-8 bytes or fewer.")

    @classmethod
    def hash_password(cls, password: str) -> str:
        cls.validate_password(password)
        pw_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(pw_bytes, salt)
        return hashed.decode("utf-8")

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        if not plain_password or not hashed_password:
            return False
        try:
            pw_bytes = plain_password.encode("utf-8")
            if len(pw_bytes) > MAX_BCRYPT_BYTES:
                return False
            hash_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(pw_bytes, hash_bytes)
        except Exception as e:
            logger.error(f"[PasswordService] Verification error: {e}")
            return False

password_service = PasswordService()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_service.verify_password(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return password_service.hash_password(password)

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
