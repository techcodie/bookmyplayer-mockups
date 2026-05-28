"""Priority scoring — powers the "Focus today" list.

This is a transparent heuristic, not a model: it folds four signals (stage,
deadline proximity, your interest, and staleness) into one number, and the
focus list is just applications sorted by it descending. The weights are a
first guess; with real usage you'd tune them by tracking which surfaced items
users actually act on.
"""

from datetime import date

from app.models import Application, Stage

# Active stages count for more; terminal/offer stages don't need daily action.
_STAGE_WEIGHT: dict[Stage, int] = {
    Stage.OFFER: 0,
    Stage.INTERVIEW: 5,
    Stage.OA: 4,
    Stage.APPLIED: 2,
    Stage.WISHLIST: 1,
    Stage.REJECTED: 0,
    Stage.GHOSTED: 0,
}


def priority_score(app: Application, today: date) -> int:
    """Higher = more urgent to act on now."""
    score = _STAGE_WEIGHT.get(app.current_stage, 0)

    # Deadline proximity: the closer (or overdue), the louder.
    if app.deadline:
        days_left = (app.deadline.date() - today).days
        if days_left <= 0:
            score += 10  # overdue / closing today
        elif days_left <= 3:
            score += 6
        elif days_left <= 7:
            score += 3

    # Your own interest (1..5) nudges ties toward what you care about.
    score += app.interest_level

    # Staleness: an application sitting in an active stage with no movement
    # is probably waiting on a follow-up from you.
    days_idle = (today - app.last_event_at.date()).days
    if app.current_stage in {Stage.APPLIED, Stage.OA} and days_idle >= 7:
        score += 4

    return score
