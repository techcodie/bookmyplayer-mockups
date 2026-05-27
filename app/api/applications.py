"""Applications router (thin). Field edits live here; stage changes are
delegated to the pipeline state machine via the dedicated /transition route."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import Application, ApplicationEvent, Stage, User
from app.repositories import applications as repo
from app.repositories import tags as tag_repo
from app.schemas import (
    ApplicationCreate,
    ApplicationDetail,
    ApplicationOut,
    ApplicationUpdate,
    EventOut,
    TagCreate,
    TagOut,
    TransitionRequest,
)
from app.services import pipeline, scoring

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=list[ApplicationOut])
def list_applications(
    stage: Stage | None = None,
    tag: str | None = None,
    search: str | None = None,
    sort: str = Query("recent", pattern="^(recent|priority|deadline)$"),
    include_archived: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    apps = repo.query_for_user(
        db, user.id, stage=stage, tag=tag, search=search,
        include_archived=include_archived,
    )
    if sort == "priority":
        today = datetime.now(timezone.utc).date()
        apps.sort(key=lambda a: scoring.priority_score(a, today), reverse=True)
    elif sort == "deadline":
        # Soonest deadline first; applications without one sink to the bottom.
        apps.sort(key=lambda a: (a.deadline is None, a.deadline or datetime.max))
    else:  # recent
        apps.sort(key=lambda a: a.created_at, reverse=True)
    return apps


@router.post("", response_model=ApplicationOut, status_code=201)
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    app = Application(
        user_id=user.id,
        current_stage=payload.initial_stage,
        last_event_at=now,
        applied_at=now if payload.initial_stage == Stage.APPLIED else None,
        **payload.model_dump(exclude={"initial_stage"}),
    )
    db.add(app)
    db.flush()  # assign app.id before seeding the event

    # Seed the event log so analytics has a starting point from day one.
    db.add(
        ApplicationEvent(
            application_id=app.id,
            from_stage=None,
            to_stage=payload.initial_stage,
            note="created",
            occurred_at=now,
        )
    )
    db.commit()
    db.refresh(app)
    return app


@router.get("/{app_id}", response_model=ApplicationDetail)
def get_application(
    app_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    app = repo.get_owned_with_events(db, app_id, user.id)
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.patch("/{app_id}", response_model=ApplicationOut)
def update_application(
    app_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    app = repo.get_owned(db, app_id, user.id)
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(app, field, value)
    db.commit()
    db.refresh(app)
    return app


@router.post("/{app_id}/transition", response_model=EventOut)
def transition_application(
    app_id: int,
    payload: TransitionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """The single enforcement point for the state machine."""
    app = repo.get_owned(db, app_id, user.id)
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    try:
        return pipeline.transition(db, app, payload.to_stage, payload.note)
    except pipeline.InvalidTransition as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{app_id}", status_code=204)
def archive_application(
    app_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Soft-delete: archive rather than destroy, so analytics history survives."""
    app = repo.get_owned(db, app_id, user.id)
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    app.archived = True
    db.commit()


@router.post("/{app_id}/tags", response_model=list[TagOut])
def add_tag(
    app_id: int,
    payload: TagCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Attach a tag (creating it for this user if it doesn't exist yet)."""
    app = repo.get_owned(db, app_id, user.id)
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    tag = tag_repo.get_or_create(db, user.id, payload.name)
    if tag not in app.tags:
        app.tags.append(tag)
        db.commit()
    return app.tags


@router.delete("/{app_id}/tags/{tag_id}", response_model=list[TagOut])
def remove_tag(
    app_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    app = repo.get_owned(db, app_id, user.id)
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    tag = tag_repo.get_owned(db, tag_id, user.id)
    if tag is not None and tag in app.tags:
        app.tags.remove(tag)
        db.commit()
    return app.tags
