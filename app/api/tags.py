"""Tags router. Tags are owned per user and reused across applications;
attaching/detaching them to an application lives on the applications router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import User
from app.repositories import tags as repo
from app.schemas import TagCreate, TagOut

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagOut])
def list_tags(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return repo.list_for_user(db, user.id)


@router.post("", response_model=TagOut, status_code=201)
def create_tag(
    payload: TagCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    tag = repo.get_or_create(db, user.id, payload.name)
    db.commit()
    db.refresh(tag)
    return tag
