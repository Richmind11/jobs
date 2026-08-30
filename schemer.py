from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ============================================================
# CREATE JOB
# ============================================================

class JobCreate(BaseModel):
    title: str
    company: str
    description: str
    location: str
    salary: Optional[str] = None
    employment_type: str = "Full-time"
    employer_id: int


# ============================================================
# UPDATE JOB
# ============================================================

class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    employment_type: Optional[str] = None


# ============================================================
# JOB RESPONSE
# ============================================================

class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    description: str
    location: str
    salary: Optional[str] = None
    employment_type: str
    employer_id: int
    is_visible: bool
    is_featured: bool
    created_at: datetime

    # Allows Pydantic to read SQLAlchemy objects
    model_config = ConfigDict(
        from_attributes=True
    )