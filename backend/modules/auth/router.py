from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.database import get_db
from core.dependencies import get_current_user
from modules.auth.schemas import (
    UserRegister, UserLogin, TokenRefresh,
    TokenResponse, RegisterResponse, UserResponse
)
from modules.auth.service import register_user, login_user, refresh_tokens, logout_user
from modules.auth.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Crée un nouveau compte utilisateur."""
    user = register_user(db, data)
    return RegisterResponse(
        message="Compte créé avec succès",
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Authentifie un utilisateur et retourne une paire JWT."""
    return login_user(db, data)


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: TokenRefresh):
    """Génère une nouvelle paire de tokens depuis un refresh token valide."""
    return refresh_tokens(data.refresh_token)


@router.post("/logout", status_code=204)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_id: str = Depends(get_current_user)
):
    """Révoque les tokens de l utilisateur connecté."""
    logout_user(access_token=credentials.credentials)
    return None


@router.get("/me", response_model=UserResponse)
def get_me(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retourne les informations de l utilisateur connecté."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable"
        )
    return UserResponse.model_validate(user)