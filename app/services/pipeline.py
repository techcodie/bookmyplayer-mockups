"""The pipeline state machine.

This is the single enforcement point for stage changes. Instead of letting a
generic update set `current_stage` to anything, every move goes through
`transition()`, which:
  1. checks the move is legal (the table below),
  2. appends an immutable event (the analytics source of truth), and
  3. updates the denormalized `current_stage` cache.

Centralizing this is exactly why the funnel can be trusted: history can never
contradict the current state.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import Application, ApplicationEvent, Stage

# Allowed moves. A stage maps to the set of stages you may move *to*.
# Terminal stages (offer / rejected / ghosted) have no outgoing moves.
ALLOWED_TRANSITIONS: dict[Stage, set[Stage]] = {
    Stage.WISHLIST: {Stage.APPLIED, Stage.REJECTED, Stage.GHOSTED},
    Stage.APPLIED: {Stage.OA, Stage.INTERVIEW, Stage.REJECTED, Stage.GHOSTED},
    Stage.OA: {Stage.INTERVIEW, Stage.REJECTED, Stage.GHOSTED},
    Stage.INTERVIEW: {Stage.OFFER, Stage.REJECTED, Stage.GHOSTED},
    Stage.OFFER: set(),
    Stage.REJECTED: set(),
    Stage.GHOSTED: set(),
}


class InvalidTransition(Exception):
    """Raised when a requested stage change isn't allowed from the current stage."""

    def __init__(self, frm: Stage, to: Stage):
        self.frm, self.to = frm, to
        super().__init__(f"Cannot move from '{frm.value}' to '{to.value}'.")


def is_allowed(frm: Stage, to: Stage) -> bool:
    return to in ALLOWED_TRANSITIONS.get(frm, set())


def transition(
    db: Session,
    application: Application,
    to_stage: Stage,
    note: str | None = None,
) -> ApplicationEvent:
    """Validate, log, and apply a stage change. Raises InvalidTransition if illegal."""
    frm = application.current_stage
    if not is_allowed(frm, to_stage):
        raise InvalidTransition(frm, to_stage)

    now = datetime.now(timezone.utc)
    event = ApplicationEvent(
        application_id=application.id,
        from_stage=frm,
        to_stage=to_stage,
        note=note,
        occurred_at=now,
    )
    db.add(event)

    # Keep the denormalized cache and a few derived fields in sync.
    application.current_stage = to_stage
    application.last_event_at = now
    if to_stage == Stage.APPLIED and application.applied_at is None:
        application.applied_at = now

    db.commit()
    db.refresh(application)
    db.refresh(event)
    return event
