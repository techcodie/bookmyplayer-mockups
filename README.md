# OfferFunnel

> Run your internship search like a pipeline — track every application through validated stages, surface what to act on today, and see exactly where you're losing offers.

A FastAPI backend for tracking internship applications as a funnel. It's deliberately **not** a CRUD spreadsheet: three pieces carry the product.

## The three cores (the parts worth defending)

1. **Pipeline state machine** — [`app/services/pipeline.py`](app/services/pipeline.py)
   Stage changes only happen through `POST /applications/{id}/transition`, which validates the move is legal, appends an immutable event, and updates a denormalized `current_stage` cache. Illegal moves return `409`.

2. **Funnel analytics** — [`app/services/analytics.py`](app/services/analytics.py)
   Counts each application by the **furthest** stage it ever reached (from the event log), so an application rejected *after* an interview still counts toward "reached Interview." Conversion = reached(next) / reached(current); the weakest step is surfaced as the biggest drop-off.

3. **Priority scoring** — [`app/services/scoring.py`](app/services/scoring.py)
   A transparent heuristic (stage + deadline proximity + interest + staleness) that powers the `GET /focus/today` "what should I act on now" list.

All three are pure functions, unit-tested in [`tests/test_cores.py`](tests/test_cores.py) without a database.

## Architecture

Thin routers → services (business logic) → repositories (data access). That separation keeps SQL in one place and the logic cores testable in isolation. A React + Vite SPA consumes the API.

```
app/                   # FastAPI backend
├── main.py            # app, CORS, router registration, table creation
├── db.py              # engine, session, get_db dependency
├── core/              # config (env-driven) + security (JWT, bcrypt)
├── models/            # SQLAlchemy 2.0 models + Stage/ReminderType enums
├── schemas/           # Pydantic v2 request/response contracts
├── api/               # routers: auth, applications, analytics, focus, reminders, tags
├── services/          # ⭐ pipeline, analytics, scoring, reminders
└── repositories/      # data access (applications, tags, reminders)
scripts/seed.py        # rich demo dataset (back-dated event histories)
frontend/              # React + Vite + Tailwind SPA
└── src/
    ├── api.ts         # typed API client (JWT in localStorage)
    ├── lib.ts         # stage metadata + state-machine mirror
    └── components/    # Board (Kanban), FocusToday, Analytics, AppDetail, …
```

Stack: **Backend** FastAPI · SQLAlchemy 2.0 · Pydantic v2 · SQLite · JWT (python-jose) · bcrypt. **Frontend** React 18 · Vite · TypeScript · Tailwind (hand-rolled funnel chart + native drag-and-drop, zero UI/chart deps).

## Run it

**Backend** (terminal 1):

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.seed          # optional: rich demo data
uvicorn app.main:app --reload   # API on :8000, docs at /docs
```

**Frontend** (terminal 2):

```bash
cd frontend
npm install
npm run dev                     # SPA on http://127.0.0.1:5173 (proxies /api -> :8000)
```

Open **http://127.0.0.1:5173** and sign in with the seeded account:

```
demo@offerfunnel.app  /  password123
```

> **VSCode:** select `.venv/bin/python` as the interpreter (Cmd+Shift+P → "Python: Select Interpreter") so imports resolve and the package hints disappear.

## Test

```bash
pip install pytest
pytest -q
```

## Key endpoints

| Method | Path | What it does |
|--------|------|--------------|
| POST | `/auth/register` · `/auth/login` | register / get a JWT |
| GET/POST | `/applications` | list / create applications |
| GET | `/applications/{id}` | detail + event timeline |
| PATCH | `/applications/{id}` | edit fields (**not** stage) |
| POST | `/applications/{id}/transition` | ⭐ the only way to change stage |
| GET | `/applications` | list with `?stage=&tag=&search=&sort=recent\|priority\|deadline` |
| GET | `/analytics/funnel` | ⭐ reach + conversion + biggest drop-off |
| GET | `/analytics/summary` | response rate, offer rate, avg time-to-response |
| GET | `/analytics/velocity` | avg time-in-stage (completed stays only) |
| GET | `/focus/today` | ⭐ priority-sorted action list |
| GET/PATCH | `/reminders` | rule-generated nudges; mark done (`?due=true` for open) |
| GET/POST | `/tags` · `/applications/{id}/tags` | manage and attach tags |

## Frontend screens

- **Pipeline** — drag-and-drop Kanban (only legal moves accepted), interest stars, deadline badges, tags.
- **Focus today** — priority-sorted action list + rule-generated reminders you can check off.
- **Analytics** — hero conversion funnel with biggest-drop-off callout, summary stat cards, velocity bars.
- **Detail modal** — full event timeline + state-machine-driven transition buttons.

## Next steps (the "with more time" roadmap)

- Alembic migrations (currently tables are auto-created on startup)
- Integration tests for the routers (the three cores are already unit-tested)
- Chrome extension for one-click save; email reminders; per-resume conversion analytics
