from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models import Stage

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str | None = None

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    name: str | None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ApplicationCreate(BaseModel):
    company: str
    role: str
    job_url: str | None = None
    location: str | None = None
    source: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    interest_level: int = Field(default=3, ge=1, le=5)
    deadline: datetime | None = None
    initial_stage: Stage = Stage.WISHLIST

class ApplicationUpdate(BaseModel):
    company: str | None = None
    role: str | None = None
    job_url: str | None = None
    location: str | None = None
    source: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    interest_level: int | None = Field(default=None, ge=1, le=5)
    deadline: datetime | None = None

class TransitionRequest(BaseModel):
    to_stage: Stage
    note: str | None = None

class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    from_stage: Stage | None
    to_stage: Stage
    note: str | None
    occurred_at: datetime

class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    company: str
    role: str
    job_url: str | None
    location: str | None
    source: str | None
    salary_min: int | None
    salary_max: int | None
    interest_level: int
    current_stage: Stage
    applied_at: datetime | None
    deadline: datetime | None
    last_event_at: datetime
    created_at: datetime
    tags: list[str] = []

class ApplicationDetail(ApplicationOut):
    events: list[EventOut] = []
