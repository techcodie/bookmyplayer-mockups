"""Data access for applications. Routers never touch the ORM query API
directly — they go through here, which keeps SQL concerns in one place."""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Application, Stage, Tag


def get_owned(db: Session, app_id: int, user_id: int) -> Application | None:
    """Fetch an application only if it belongs to this user (scoped query)."""
    stmt = select(Application).where(
        Application.id == app_id, Application.user_id == user_id
    )
    return db.scalar(stmt)


def get_owned_with_events(db: Session, app_id: int, user_id: int) -> Application | None:
    stmt = (
        select(Application)
        .where(Application.id == app_id, Application.user_id == user_id)
        .options(selectinload(Application.events))
    )
    return db.scalar(stmt)


def list_for_user(
    db: Session, user_id: int, include_archived: bool = False
) -> list[Application]:
    stmt = (
        select(Application)
        .where(Application.user_id == user_id)
        .options(selectinload(Application.tags))
    )
    if not include_archived:
        stmt = stmt.where(Application.archived.is_(False))
    return list(db.scalars(stmt))


def query_for_user(
    db: Session,
    user_id: int,
    *,
    stage: Stage | None = None,
    tag: str | None = None,
    search: str | None = None,
    include_archived: bool = False,
) -> list[Application]:
    """Filtered list used by the board/table view. Sorting (incl. priority)
    happens in the router; SQL handles the predicates."""
    stmt = (
        select(Application)
        .where(Application.user_id == user_id)
        .options(selectinload(Application.tags))
    )
    if not include_archived:
        stmt = stmt.where(Application.archived.is_(False))
    if stage is not None:
        stmt = stmt.where(Application.current_stage == stage)
    if tag:
        stmt = stmt.join(Application.tags).where(Tag.name == tag)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(Application.company.ilike(pattern), Application.role.ilike(pattern))
        )
    return list(db.scalars(stmt))


def list_with_events(db: Session, user_id: int) -> list[Application]:
    """Used by analytics — loads events eagerly to avoid N+1 queries."""
    stmt = (
        select(Application)
        .where(Application.user_id == user_id, Application.archived.is_(False))
        .options(selectinload(Application.events))
    )
    return list(db.scalars(stmt))
