"""SQLAlchemy ORM models (SQLAlchemy 2.0 typed style).

Design note worth saying out loud in an interview:
`Application.current_stage` is a *denormalized cache* so the board renders
fast, while `application_events` is the append-only *source of truth* for the
funnel and time-in-stage analytics. The two are kept in sync only through the
pipeline service's `/transition` path.
"""

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Stage(str, Enum):
    """The stages an application can occupy. Stored as the string value."""

    WISHLIST = "wishlist"
    APPLIED = "applied"
    OA = "oa"  # online assessment
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    GHOSTED = "ghosted"


class ReminderType(str, Enum):
    """The kinds of rule-generated reminders the focus engine can raise."""

    FOLLOW_UP = "follow_up"  # stale application waiting on a nudge from you
    DEADLINE = "deadline"    # an application deadline is closing
    INTERVIEW = "interview"  # an upcoming interview to prepare for


# Many-to-many: an application can carry many tags; a tag many applications.
application_tags = Table(
    "application_tags",
    Base.metadata,
    Column("application_id", ForeignKey("applications.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    applications: Mapped[list["Application"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    company: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(200))
    job_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    salary_min: Mapped[int | None] = mapped_column(nullable=True)
    salary_max: Mapped[int | None] = mapped_column(nullable=True)
    interest_level: Mapped[int] = mapped_column(default=3)  # 1..5

    # Denormalized cache of the latest stage (see module docstring).
    current_stage: Mapped[Stage] = mapped_column(default=Stage.WISHLIST)

    applied_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Timestamp of the most recent event; powers staleness in priority scoring.
    last_event_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
    archived: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship(back_populates="applications")
    events: Mapped[list["ApplicationEvent"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="ApplicationEvent.occurred_at",
    )
    tags: Mapped[list["Tag"]] = relationship(
        secondary=application_tags, back_populates="applications"
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )


class ApplicationEvent(Base):
    """Append-only log of stage transitions. The analytics source of truth."""

    __tablename__ = "application_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id"), index=True
    )
    from_stage: Mapped[Stage | None] = mapped_column(nullable=True)
    to_stage: Mapped[Stage] = mapped_column()
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    application: Mapped["Application"] = relationship(back_populates="events")


class Tag(Base):
    """A user-defined label (e.g. 'remote', 'dream', 'backend')."""

    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_tag_user_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(60))

    applications: Mapped[list["Application"]] = relationship(
        secondary=application_tags, back_populates="tags"
    )


class Reminder(Base):
    """A rule-generated nudge. Generated idempotently per (application, type);
    the rules themselves live in the pure `services.reminders` core."""

    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id"), index=True
    )
    type: Mapped[ReminderType] = mapped_column()
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    message: Mapped[str] = mapped_column(String(300))
    is_done: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    application: Mapped["Application"] = relationship(back_populates="reminders")
