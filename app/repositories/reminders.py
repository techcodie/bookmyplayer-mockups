"""Data access for reminders. Reminders belong to a user transitively through
their application, so every query joins back to enforce ownership."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Application, Reminder, ReminderType


def list_for_user(db: Session, user_id: int, only_open: bool = False) -> list[Reminder]:
    stmt = (
        select(Reminder)
        .join(Application, Reminder.application_id == Application.id)
        .where(Application.user_id == user_id)
        .order_by(Reminder.due_at)
    )
    if only_open:
        stmt = stmt.where(Reminder.is_done.is_(False))
    return list(db.scalars(stmt))


def existing_types(db: Session, application_id: int) -> set[ReminderType]:
    """Reminder types already recorded for an application — used to keep
    generation idempotent (one live reminder per application+type)."""
    rows = db.scalars(
        select(Reminder.type).where(Reminder.application_id == application_id)
    )
    return set(rows)


def get_owned(db: Session, reminder_id: int, user_id: int) -> Reminder | None:
    return db.scalar(
        select(Reminder)
        .join(Application, Reminder.application_id == Application.id)
        .where(Reminder.id == reminder_id, Application.user_id == user_id)
    )
