"""Rule-based reminders — the nudge engine behind the focus workflow.

Deliberately simple: a transparent set of rules turns an application's state
into zero or more reminders. There's no message queue and no scheduler — at a
single user's scale that would be premature complexity. The router *generates*
reminders idempotently on read (one per application+type) and persists them so
they can be marked done; these rules are the pure, unit-testable core.
"""

from dataclasses import dataclass
from datetime import date, datetime, timezone

from app.models import ReminderType, Stage

# After this many idle days in an active-waiting stage, nudge a follow-up.
FOLLOW_UP_AFTER_DAYS = 7
# Surface a deadline reminder once it's within this many days (or overdue).
DEADLINE_WITHIN_DAYS = 3
# Stages that don't warrant a reminder (the search has concluded for them).
_INACTIVE = {Stage.OFFER, Stage.REJECTED, Stage.GHOSTED}
# Stages where silence usually means the ball is in your court.
_WAITING = {Stage.APPLIED, Stage.OA}


@dataclass
class CandidateReminder:
    type: ReminderType
    message: str
    due_at: datetime


def generate_for(app, today: date) -> list[CandidateReminder]:
    """Return the reminders an application warrants today (possibly none).

    `app` needs: current_stage, company, role, deadline, last_event_at.
    Kept duck-typed so it's testable with a plain object, like scoring.
    """
    if app.current_stage in _INACTIVE:
        return []

    out: list[CandidateReminder] = []

    # Deadline closing (or already overdue).
    if app.deadline is not None:
        days_left = (app.deadline.date() - today).days
        if days_left <= DEADLINE_WITHIN_DAYS:
            when = "overdue" if days_left < 0 else (
                "today" if days_left == 0 else f"in {days_left}d"
            )
            out.append(
                CandidateReminder(
                    type=ReminderType.DEADLINE,
                    message=f"{app.company} — {app.role} deadline {when}",
                    due_at=app.deadline,
                )
            )

    # Stale application waiting on a follow-up from you.
    days_idle = (today - app.last_event_at.date()).days
    if app.current_stage in _WAITING and days_idle >= FOLLOW_UP_AFTER_DAYS:
        out.append(
            CandidateReminder(
                type=ReminderType.FOLLOW_UP,
                message=f"Follow up with {app.company} — no movement in {days_idle}d",
                due_at=app.last_event_at,
            )
        )

    # An interview to prepare for.
    if app.current_stage == Stage.INTERVIEW:
        out.append(
            CandidateReminder(
                type=ReminderType.INTERVIEW,
                message=f"Prep for your {app.company} interview ({app.role})",
                due_at=app.deadline or datetime.now(timezone.utc),
            )
        )

    return out
