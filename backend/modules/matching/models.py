import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cv_id = Column(UUID(as_uuid=True), ForeignKey("cvs.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    score = Column(Float, nullable=False)           # score 0.0 à 100.0
    skills_score = Column(Float, nullable=True)     # score compétences (60%)
    title_score = Column(Float, nullable=True)      # score titre (25%)
    exp_score = Column(Float, nullable=True)        # score expérience (15%)
    matched_skills = Column(JSON, nullable=True)    # skills en commun
    missing_skills = Column(JSON, nullable=True)    # skills manquants
    computed_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relations
    cv = relationship("CV", back_populates="matches")
    job = relationship("Job", back_populates="matches")