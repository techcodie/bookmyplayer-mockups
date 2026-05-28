"""Pydantic v2 request/response models — the API's typed contract."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models import ReminderType, Stage


# ---- Auth ----
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


# ---- Applications ----
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
    # Optional starting stage; defaults to wishlist.
    initial_stage: Stage = Stage.WISHLIST


class ApplicationUpdate(BaseModel):
    """Edit fields — note this deliberately cannot change the stage.
    Stage changes only happen via POST /applications/{id}/transition."""

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

    @field_validator("tags", mode="before")
    @classmethod
    def _tag_names(cls, v):
        """Accept the ORM's list[Tag] and project it down to plain names."""
        if not v:
            return []
        return [t if isinstance(t, str) else t.name for t in v]


class ApplicationDetail(ApplicationOut):
    events: list[EventOut] = []


class FocusItem(ApplicationOut):
    priority_score: int


# ---- Analytics ----
class FunnelStepOut(BaseModel):
    stage: str
    reached: int
    conversion: float | None


class FunnelOut(BaseModel):
    steps: list[FunnelStepOut]
    biggest_dropoff: dict | None


class SummaryOut(BaseModel):
    total: int
    active: int
    applied: int
    responded: int
    offers: int
    response_rate: float | None
    offer_rate: float | None
    avg_time_to_response_days: float | None


class VelocityStepOut(BaseModel):
    stage: str
    avg_days: float
    n: int


# ---- Tags ----
class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=60)


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


# ---- Reminders ----
class ReminderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    application_id: int
    type: ReminderType
    due_at: datetime
    message: str
    is_done: bool


class ReminderUpdate(BaseModel):
    is_done: bool
