from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Moteur de connexion PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,     # vérifie que la connexion est vivante avant chaque requête
    pool_size=10,           # nombre de connexions simultanées max
    max_overflow=20,        # connexions supplémentaires si pool plein
    echo=settings.DEBUG     # log les requêtes SQL uniquement en mode DEBUG
)

# Session factory — une session = une transaction
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Classe de base pour tous les modèles SQLAlchemy
Base = declarative_base()


def get_db():
    """
    Dependency injection FastAPI — fournit une session DB par requête.
    La session est automatiquement fermée après chaque requête.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()