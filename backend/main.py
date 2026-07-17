from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from core.config import settings
from core.database import Base, engine
import structlog
# Import des modèles pour que SQLAlchemy crée les tables
from modules.auth.models import User
from modules.cv.models import CV
from modules.jobs.models import Job
from modules.matching.models import Match
# Initialize structured logging. Using structlog ensures clean, machine-readable 
# JSON logs in production (perfect for ELK, Loki, or Datadog ingestion).
logger = structlog.get_logger()


# ─── STARTUP / SHUTDOWN (ASGI LIFESPAN) ──────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application lifecycle via the ASGI Lifespan protocol.
    
    Use this context manager to safely initialize and release shared system resources 
    (e.g., HTTP client sessions, database connection pools, or ML model weights) 
    to prevent connection leaks and ensure graceful termination on SIGTERM.
    """
    logger.info("Starting JobMatch AI", version=settings.APP_VERSION)
    
    # NOTE: DDL generation via SQLAlchemy is commented out below.
    # In production, schema migrations should be managed externally using Alembic 
    # to maintain database state history and avoid race conditions during horizontal scaling.
    Base.metadata.create_all(bind=engine)  # Activé après install PostgreSQL
    
    logger.info("JobMatch AI started successfully")
    yield  # Control yields here; the application is actively serving traffic
    
    # Cleanup phase executed during application teardown
    logger.info("Shutting down JobMatch AI")


# ─── APPLICATION INITIALIZATION ──────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de matching CV/offres d emploi pour le marché tunisien",
    # Exposing interactive API docs only in DEBUG mode reduces the production attack 
    # surface and prevents unauthorized reverse-engineering of the endpoints.
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)


# ─── SECURITY MIDDLEWARES ────────────────────────────────────────────────────

# CORS (Cross-Origin Resource Sharing) Configuration:
# Enforces the Same-Origin Policy by explicitly listing trusted origins.
# Security Note: credentials=True is set, meaning ALLOWED_ORIGINS must be 
# concrete domains (no wildcards '*') to prevent credential theft.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Host Header Validation:
# Defends against HTTP Host Header Injection and Web Cache Poisoning attacks 
# by dropping any incoming requests where the host header doesn't match this whitelist.
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.railway.app", "*.render.com"]
)


# ─── OPERATIONAL / MONITORING ENDPOINTS ──────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    """
    Metadata / Landing Endpoint.
    
    Returns basic application info. Helpful for manual smoke testing 
    immediately after a deployment pipeline runs.
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Liveness / Readiness Probe.
    
    A lightweight, unauthenticated endpoint utilized by container orchestrators 
    (like Kubernetes, Railway, or AWS ECS) and load balancers to monitor 
    container health and trigger automatic rollbacks or restarts.
    """
    return {"status": "healthy"}