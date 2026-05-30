"""Reminders router.

`GET /reminders` lazily *generates* reminders from the rule engine and persists
any that don't exist yet (idempotent per application+type), then returns the
list. Marking one done is a simple PATCH. No scheduler is involved — at this
scale, generating on read is both simpler and impossible to drift out of sync.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import Reminder, Stage, User
from app.repositories import applications as app_repo
from app.repositories import reminders as repo
from app.schemas import ReminderOut, ReminderUpdate
from app.services import reminders as engine

# Stages that never warrant reminders (mirrors the engine's view).
_INACTIVE = {Stage.OFFER, Stage.REJECTED, Stage.GHOSTED}


def _sync(db: Session, user_id: int) -> None:
    """Generate missing reminders for the user's active applications."""
    today = datetime.now(timezone.utc).date()
    created = False
    for app in app_repo.list_for_user(db, user_id):
        if app.current_stage in _INACTIVE:
            continue
        already = repo.existing_types(db, app.id)
        for candidate in engine.generate_for(app, today):
            if candidate.type in already:
                continue  # keep generation idempotent per application+type
            db.add(
                Reminder(
                    application_id=app.id,
                    type=candidate.type,
                    due_at=candidate.due_at,
                    message=candidate.message,
                )
            )
            already.add(candidate.type)
            created = True
    if created:
        db.commit()


router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("", response_model=list[ReminderOut])
def list_reminders(
    due: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _sync(db, user.id)
    return repo.list_for_user(db, user.id, only_open=due)


@router.patch("/{reminder_id}", response_model=ReminderOut)
def update_reminder(
    reminder_id: int,
    payload: ReminderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    reminder = repo.get_owned(db, reminder_id, user.id)
    if reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    reminder.is_done = payload.is_done
    db.commit()
    db.refresh(reminder)
    return reminder
