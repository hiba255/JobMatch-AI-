from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID
from datetime import datetime


# ─── REQUEST SCHEMAS ─────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        return v

    @field_validator('full_name')
    @classmethod
    def full_name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Le nom complet ne peut pas être vide')
        return v.strip()


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenRefresh(BaseModel):
    refresh_token: str


# ─── RESPONSE SCHEMAS ────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse