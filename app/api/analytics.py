"""Analytics router. Pulls applications + their events, derives each one's
furthest stage, and hands plain data to the pure funnel function."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import User
from app.repositories import applications as repo
from app.schemas import FunnelOut, SummaryOut, VelocityStepOut
from app.services import analytics

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _histories(apps) -> list[list[tuple]]:
    """Project each application's event log into the ordered (stage, when)
    history the summary/velocity cores consume."""
    return [[(ev.to_stage, ev.occurred_at) for ev in app.events] for app in apps]


@router.get("/funnel", response_model=FunnelOut)
def funnel(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    apps = repo.list_with_events(db, user.id)

    # For each application, collect every stage it ever touched (from its event
    # log) and reduce to the furthest funnel index it reached.
    furthest_indices = [
        analytics.furthest_index(ev.to_stage for ev in app.events) for app in apps
    ]

    result = analytics.compute_funnel(furthest_indices)
    return FunnelOut(
        steps=[vars(s) for s in result.steps],
        biggest_dropoff=result.biggest_dropoff,
    )


@router.get("/summary", response_model=SummaryOut)
def summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    apps = repo.list_with_events(db, user.id)
    result = analytics.compute_summary(_histories(apps))
    return SummaryOut(**vars(result))


@router.get("/velocity", response_model=list[VelocityStepOut])
def velocity(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    apps = repo.list_with_events(db, user.id)
    return [vars(s) for s in analytics.compute_velocity(_histories(apps))]
