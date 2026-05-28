"""FastAPI app entrypoint: CORS, router registration, and table creation.

For the MVP we create tables on startup via `Base.metadata.create_all`. The
next step (noted in the README) is to switch to Alembic migrations so schema
changes are versioned.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db import Base, engine

# Import models so they're registered on Base before create_all runs.
from app import models  # noqa: F401
from app.api import analytics, applications, auth, focus, reminders, tags


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="OfferFunnel", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(analytics.router)
app.include_router(focus.router)
app.include_router(reminders.router)
app.include_router(tags.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
