"""Focus router — the 'what should I act on today' list. Scores every active
application and returns them sorted by urgency. This is what separates the
product from a spreadsheet."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import Stage, User
from app.repositories import applications as repo
from app.schemas import ApplicationOut, FocusItem
from app.services import scoring

router = APIRouter(prefix="/focus", tags=["focus"])

# Stages that are "done" and don't need daily attention.
_INACTIVE = {Stage.OFFER, Stage.REJECTED, Stage.GHOSTED}


@router.get("/today", response_model=list[FocusItem])
def focus_today(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    today = datetime.now(timezone.utc).date()
    apps = [
        a for a in repo.list_for_user(db, user.id) if a.current_stage not in _INACTIVE
    ]

    scored = [
        FocusItem(
            **ApplicationOut.model_validate(a).model_dump(),
            priority_score=scoring.priority_score(a, today),
        )
        for a in apps
    ]
    scored.sort(key=lambda item: item.priority_score, reverse=True)
    return scored
