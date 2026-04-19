from datetime import datetime, timedelta, timezone

from jose import jwt
from pwdlib import PasswordHash

from app.core.config import settings


password_hash = PasswordHash.recommended()


def verificar_password(password_plano: str, password_hash_guardado: str) -> bool:
    return password_hash.verify(password_plano, password_hash_guardado)


def obtener_password_hash(password: str) -> str:
    return password_hash.hash(password)


def crear_token_access(data: dict):
    datos = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    datos.update({"exp": expire})
    return jwt.encode(datos, settings.secret_key, algorithm=settings.algorithm)