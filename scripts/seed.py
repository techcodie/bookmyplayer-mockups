"""Seed a rich demo dataset so every screen (board, funnel, focus, reminders)
has something meaningful to show.

Events are written directly with back-dated timestamps — something the API
deliberately won't let you do — so funnel/velocity/time-to-response look real.

Run from the project root:  python -m scripts.seed
Logs in with:  demo@offerfunnel.app / password123
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.security import hash_password
from app.db import Base, SessionLocal, engine
from app.models import Application, ApplicationEvent, Stage, Tag, User

DEMO_EMAIL = "demo@offerfunnel.app"
DEMO_PASSWORD = "password123"

NOW = datetime.now(timezone.utc)


def _ago(days: float) -> datetime:
    return NOW - timedelta(days=days)


def _in(days: float) -> datetime:
    return NOW + timedelta(days=days)


# (company, role, path[(stage, days_ago)], extras)
# path is oldest-first; the last entry is the current stage.
APPS = [
    # --- Wishlist (researched, not yet applied) ---
    ("Jane Street", "Quant Trading Intern", [(Stage.WISHLIST, 5)],
     dict(interest=5, deadline=2, source="careers page", tags=["dream"])),
    ("Citadel", "SWE Intern", [(Stage.WISHLIST, 8)],
     dict(interest=4, deadline=10, source="LinkedIn")),
    ("OpenAI", "Research Intern", [(Stage.WISHLIST, 2)],
     dict(interest=5, tags=["dream"])),

    # --- Applied, awaiting (some stale -> follow-up) ---
    ("Stripe", "Backend Intern", [(Stage.WISHLIST, 40), (Stage.APPLIED, 30)],
     dict(interest=4, source="referral", salary=(45, 60), tags=["backend"])),
    ("Notion", "Fullstack Intern", [(Stage.APPLIED, 12)], dict(interest=3)),
    ("Datadog", "SWE Intern", [(Stage.APPLIED, 5)],
     dict(interest=3, deadline=2, source="LinkedIn")),
    ("Airbnb", "Frontend Intern", [(Stage.WISHLIST, 20), (Stage.APPLIED, 3)],
     dict(interest=4)),

    # --- Reached OA ---
    ("Figma", "Product Eng Intern",
     [(Stage.WISHLIST, 35), (Stage.APPLIED, 28), (Stage.OA, 21)],
     dict(interest=5, tags=["design"])),
    ("Coinbase", "SWE Intern",
     [(Stage.APPLIED, 18), (Stage.OA, 10)], dict(interest=3)),
    ("Plaid", "Backend Intern",
     [(Stage.APPLIED, 25), (Stage.OA, 15)],
     dict(interest=4, deadline=1, salary=(40, 52))),

    # --- Reached Interview ---
    ("Databricks", "SWE Intern",
     [(Stage.WISHLIST, 50), (Stage.APPLIED, 40), (Stage.OA, 30), (Stage.INTERVIEW, 12)],
     dict(interest=5, salary=(50, 65), tags=["dream"])),
    ("Snowflake", "Data Eng Intern",
     [(Stage.APPLIED, 33), (Stage.OA, 24), (Stage.INTERVIEW, 6)], dict(interest=4)),
    ("Ramp", "Fullstack Intern",
     [(Stage.APPLIED, 28), (Stage.INTERVIEW, 14)], dict(interest=4)),

    # --- Offer ---
    ("Linear", "Frontend Intern",
     [(Stage.WISHLIST, 60), (Stage.APPLIED, 52), (Stage.OA, 44),
      (Stage.INTERVIEW, 30), (Stage.OFFER, 18)],
     dict(interest=5, salary=(42, 55), tags=["dream"])),

    # --- Rejected at various depths (still count toward reach) ---
    ("Google", "STEP Intern",
     [(Stage.APPLIED, 45), (Stage.OA, 35), (Stage.REJECTED, 28)], dict(interest=4)),
    ("Meta", "SWE Intern",
     [(Stage.WISHLIST, 55), (Stage.APPLIED, 48), (Stage.INTERVIEW, 40),
      (Stage.REJECTED, 33)], dict(interest=5)),
    ("Amazon", "SDE Intern",
     [(Stage.APPLIED, 50), (Stage.REJECTED, 46)], dict(interest=2)),

    # --- Ghosted (no response) ---
    ("Roblox", "Gameplay Intern",
     [(Stage.APPLIED, 38), (Stage.GHOSTED, 10)], dict(interest=2)),
]


def reset_demo_user(db) -> User:
    existing = db.scalar(select(User).where(User.email == DEMO_EMAIL))
    if existing:
        db.delete(existing)  # cascades to applications/events/reminders
        db.commit()
    user = User(
        email=DEMO_EMAIL,
        password_hash=hash_password(DEMO_PASSWORD),
        name="Demo Student",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def seed_app(db, user, company, role, path, extras):
    deadline = _in(extras["deadline"]) if "deadline" in extras else None
    salary = extras.get("salary")
    app = Application(
        user_id=user.id,
        company=company,
        role=role,
        location=extras.get("location"),
        source=extras.get("source"),
        interest_level=extras.get("interest", 3),
        salary_min=salary[0] if salary else None,
        salary_max=salary[1] if salary else None,
        current_stage=path[-1][0],
        deadline=deadline,
        created_at=_ago(path[0][1]),
        last_event_at=_ago(path[-1][1]),
    )
    db.add(app)
    db.flush()

    prev = None
    for stage, days_ago in path:
        occurred = _ago(days_ago)
        db.add(ApplicationEvent(
            application_id=app.id,
            from_stage=prev,
            to_stage=stage,
            note="created" if prev is None else None,
            occurred_at=occurred,
        ))
        if stage == Stage.APPLIED and app.applied_at is None:
            app.applied_at = occurred
        prev = stage

    for name in extras.get("tags", []):
        tag = db.scalar(
            select(Tag).where(Tag.user_id == user.id, Tag.name == name)
        )
        if tag is None:
            tag = Tag(user_id=user.id, name=name)
            db.add(tag)
            db.flush()
        app.tags.append(tag)


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = reset_demo_user(db)
        for company, role, path, extras in APPS:
            seed_app(db, user, company, role, path, extras)
        db.commit()
        print(f"Seeded {len(APPS)} applications for {DEMO_EMAIL} / {DEMO_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
