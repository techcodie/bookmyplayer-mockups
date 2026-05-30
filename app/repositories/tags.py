"""Data access for tags."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Tag


def list_for_user(db: Session, user_id: int) -> list[Tag]:
    return list(db.scalars(select(Tag).where(Tag.user_id == user_id)))


def get_owned(db: Session, tag_id: int, user_id: int) -> Tag | None:
    return db.scalar(
        select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id)
    )


def get_or_create(db: Session, user_id: int, name: str) -> Tag:
    """Tags are unique per (user, name); reuse an existing one if present."""
    name = name.strip()
    tag = db.scalar(
        select(Tag).where(Tag.user_id == user_id, Tag.name == name)
    )
    if tag is None:
        tag = Tag(user_id=user_id, name=name)
        db.add(tag)
        db.flush()
    return tag
