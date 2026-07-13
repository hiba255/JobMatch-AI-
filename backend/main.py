from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from core.config import settings
from core.database import Base, engine
import structlog

logger = structlog.get_logger()


# ─── STARTUP / SHUTDOWN ─────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting JobMatch AI", version=settings.APP_VERSION)
    Base.metadata.create_all(bind=engine)  # activé après install PostgreSQL
    logger.info("JobMatch AI started successfully")
    yield
    logger.info("Shutting down JobMatch AI")


# ─── APPLICATION ────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de matching CV/offres d emploi pour le marché tunisien",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)


# ─── MIDDLEWARES ─────────────────────────────────────────────────────────────

# CORS — origines autorisées uniquement
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Trusted hosts — rejette les requêtes avec Host header inconnu
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.railway.app", "*.render.com"]
)


# ─── ROUTES DE BASE ──────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}