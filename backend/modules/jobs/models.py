import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False, index=True)
    company = Column(String, nullable=False)
    location = Column(String, nullable=True)
    description = Column(String, nullable=False)
    required_skills = Column(JSON, nullable=True)   # liste de skills
    experience_years = Column(Integer, nullable=True)
    education_level = Column(String, nullable=True)
    source = Column(String, default="tanitjobs")    # source du scraping
    source_url = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relations
    matches = relationship("Match", back_populates="job")