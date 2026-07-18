from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from core.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from core.config import settings
from modules.auth.models import User
from modules.auth.schemas import UserRegister, UserLogin, TokenResponse
import redis
import uuid

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


# ─── REGISTER ────────────────────────────────────────────────────────────────

def register_user(db: Session, data: UserRegister) -> User:
    """
    Crée un nouveau compte utilisateur.
    Vérifie que l email n est pas déjà utilisé avant d insérer.
    """
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte avec cet email existe déjà"
        )

    user = User(
        email=data.email,
        full_name=data.full_name,
        password_hash=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ─── LOGIN ───────────────────────────────────────────────────────────────────

def login_user(db: Session, data: UserLogin) -> TokenResponse:
    """
    Authentifie un utilisateur et retourne une paire de tokens JWT.
    Protection brute force : 5 tentatives max par email, lockout 15min.
    """
    lockout_key = f"lockout:{data.email}"
    attempts_key = f"attempts:{data.email}"

    # Vérifier lockout
    if redis_client.get(lockout_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Compte temporairement bloqué. Réessayez dans 15 minutes."
        )

    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        # Incrémenter compteur tentatives
        attempts = redis_client.incr(attempts_key)
        redis_client.expire(attempts_key, 900)  # 15 minutes

        if int(attempts) >= 5:
            redis_client.set(lockout_key, "1", ex=900)
            redis_client.delete(attempts_key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Trop de tentatives. Compte bloqué 15 minutes."
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    # Reset compteur après succès
    redis_client.delete(attempts_key)

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


# ─── REFRESH ─────────────────────────────────────────────────────────────────

def refresh_tokens(refresh_token: str) -> TokenResponse:
    """
    Génère une nouvelle paire de tokens depuis un refresh token valide.
    Rotation obligatoire : l ancien refresh token est révoqué après usage.
    """
    payload = verify_token(refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalide ou expiré"
        )

    # Vérifier blacklist
    if redis_client.get(f"blacklist:{refresh_token}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token révoqué"
        )

    user_id = payload.get("sub")

    # Révoquer l ancien refresh token
    from jose import jwt
    exp = payload.get("exp")
    redis_client.set(f"blacklist:{refresh_token}", "1", ex=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)

    new_access = create_access_token({"sub": user_id})
    new_refresh = create_refresh_token({"sub": user_id})

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh
    )


# ─── LOGOUT ──────────────────────────────────────────────────────────────────

def logout_user(access_token: str, refresh_token: str = None):
    """
    Révoque les tokens en les ajoutant à la blacklist Redis.
    TTL = durée restante du token pour ne pas surcharger Redis.
    """
    payload = verify_token(access_token, token_type="access")
    if payload:
        exp = payload.get("exp")
        import time
        ttl = max(int(exp - time.time()), 1)
        redis_client.set(f"blacklist:{access_token}", "1", ex=ttl)

    if refresh_token:
        redis_client.set(
            f"blacklist:{refresh_token}", "1",
            ex=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
        )