from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import verify_token
from core.config import settings
import redis

# Schéma Bearer token — extrait le JWT du header Authorization
security = HTTPBearer()

# Client Redis — pour vérifier la blacklist des tokens révoqués
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Dépendance principale — vérifie le JWT sur chaque route protégée.
    1. Extrait le token du header Authorization: Bearer <token>
    2. Vérifie que le token n est pas dans la blacklist Redis (logout)
    3. Décode et valide le JWT
    4. Retourne le user_id extrait du token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    # Vérifier blacklist Redis — token révoqué après logout
    if redis_client.get(f"blacklist:{token}"):
        raise credentials_exception

    # Décoder le JWT
    payload = verify_token(token, token_type="access")
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    return user_id


def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        HTTPBearer(auto_error=False)
    ),
):
    """
    Dépendance optionnelle — retourne user_id si token valide, None sinon.
    Utilisé pour les routes publiques qui peuvent aussi être personnalisées.
    """
    if credentials is None:
        return None

    payload = verify_token(credentials.credentials, token_type="access")
    if payload is None:
        return None

    return payload.get("sub")