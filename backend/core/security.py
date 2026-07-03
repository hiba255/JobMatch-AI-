from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from core.config import settings

# Contexte bcrypt pour hashing des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─── PASSWORDS ──────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt cost factor 12."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie qu un mot de passe correspond à son hash bcrypt."""
    return pwd_context.verify(plain_password, hashed_password)


# ─── JWT TOKENS ─────────────────────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    """
    Crée un JWT access token — expire dans 15 minutes.
    Court par sécurité : si volé, inutilisable rapidement.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def create_refresh_token(data: dict) -> str:
    """
    Crée un JWT refresh token — expire dans 7 jours.
    Utilisé uniquement pour obtenir un nouveau access token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """
    Vérifie et décode un JWT token.
    Retourne le payload si valide, None si invalide ou expiré.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None