import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base


class CV(Base):
    __tablename__ = "cvs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending/processing/done/error
    extracted_text = Column(String, nullable=True)
    entities = Column(JSON, nullable=True)  # entités NER extraites
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relations
    user = relationship("User", back_populates="cvs")
    matches = relationship("Match", back_populates="cv", cascade="all, delete-orphan")