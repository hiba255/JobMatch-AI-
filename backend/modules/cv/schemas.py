from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Any


# ─── RESPONSE SCHEMAS ────────────────────────────────────────────────────────

class CVResponse(BaseModel):
    id: UUID
    filename: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CVStatusResponse(BaseModel):
    id: UUID
    filename: str
    status: str  # pending / processing / done / error
    entities: Optional[Any] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CVListResponse(BaseModel):
    cvs: list[CVResponse]
    total: int