# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HEMA Training Calendar - training attendance tracking system for Historical European Martial Arts with QR code check-in.

**Tech Stack:** FastAPI + PostgreSQL + SQLAlchemy (backend) + React + MUI (frontend)

## Development Commands

### Environment Setup
```bash
# Install dependencies using uv
uv sync

# Activate virtual environment (if needed)
source .venv/bin/activate
```

### Running the Application
```bash
# Run development server (set PYTHONPATH to src directory)
cd /home/myrik/work/my/hema
PYTHONPATH=/home/myrik/work/my/hema/src python src/hema/main.py
# or
PYTHONPATH=/home/myrik/work/my/hema/src uvicorn hema.main:api --reload --host 0.0.0.0 --port 8000

# Run frontend dev server (separate terminal)
cd frontend && npm run dev  # Vite on http://localhost:5173

# Health check
curl http://localhost:8000/health
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_events.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=.
```

### Code Quality
```bash
# Format code with black
black .
```

### Database Operations
```bash
# Alembic migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

## Code Architecture

### Application Structure

```
hema/
├── main.py              # FastAPI application entry point + SPA fallback
├── config.py            # Pydantic settings (DB_URI, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES)
├── auth.py              # JWT auth: OAuthPasswordBearer, password hashing (Argon2), create_jwt_token
├── db.py                # Database connection and session management
├── models/              # SQLAlchemy models
│   ├── base.py         # Base declarative class with shared metadata
│   ├── users.py        # UserModel
│   ├── trainers.py     # TrainerModel (FK → users.id, marks user as trainer)
│   ├── events.py       # EventModel (training sessions)
│   ├── visits.py       # VisitModel (QR scan records)
│   ├── intentions.py   # IntentionModel (planned attendance)
│   ├── weekly_events.py # WeeklyEventModel (recurring event templates)
│   └── payments.py     # UserPaymentHistory
├── schemas/             # Pydantic schemas for API validation
│   ├── events.py       # EventBase, EventResponse, EventCreateSchema
│   ├── weekly_events.py # WeeklyEventCreate, WeeklyEventUpdate, WeeklyEventResponse
│   ├── users.py        # UserCreateSchema, UserResponseSchema, AuthResponseModel
│   ├── visits.py       # VisitResponse
│   ├── intentions.py   # intention schemas
│   ├── payments.py     # PaymentResponseSchema, PaymentUpdateSchema
│   └── schedule.py     # ScheduleEntry
├── routers/             # API route handlers
│   ├── __init__.py     # api_router (prefix /api), includes all sub-routers
│   ├── events.py       # Event CRUD endpoints
│   ├── weekly_events.py # WeeklyEvent CRUD endpoints
│   ├── schedule.py     # Schedule view (weekly events by date range)
│   ├── users.py        # User registration, login, profile
│   ├── visits.py       # Visit history for current user
│   ├── intentions.py   # Intentions CRUD
│   ├── payments.py     # Balance and payment history
├── services/            # Business logic layer
│   ├── event.py        # EventService
│   ├── weekly_event_service.py # WeeklyEventService (recurring event management)
│   ├── user_service.py # UserService
│   ├── visit_service.py # VisitService
│   ├── intention_service.py # IntentionService
│   └── payment_service.py # PaymentService
└── (no templates/ — frontend is React SPA)

frontend/                # React SPA (Vite + MUI)
├── src/
│   ├── App.tsx         # Routes: /login, /register, /, /calendar/:monday, /profile, /history
│   ├── pages/          # LoginPage, RegisterPage, CalendarPage, ProfilePage, HistoryPage
│   ├── components/     # Layout, ProtectedRoute, CalendarGrid, EventDetailSheet, ...
│   ├── contexts/       # AuthContext (JWT storage)
│   ├── api/            # API client, auth.ts, client.ts
│   └── types/          # TypeScript types
└── dist/               # Built SPA, served by FastAPI (fallback: /{path:path})
```

### Data Model Relationships

1. **Users** - user accounts
   - Fields: id, username, name, password (Argon2 hash), phone, gender
   - Gender: `m`, `f`, `o` (StrEnum)

2. **Trainers** - marks a user as a trainer
   - Single FK column: `id → users.id` (primary key)
   - Used as FK target in events and payments

3. **Events** - individual training sessions
   - Fields: id, name, color (6-char hex), date (Date), time_start (Time), time_end (Time), weekly_id, trainer_id, price
   - `trainer_id → trainers.id` (FK, SET NULL on delete)
   - `weekly_id → weekly_events.id` (FK, CASCADE on delete)
   - Color stored as 6-character hex (e.g., "4CAF50")

4. **WeeklyEvents** - recurring event templates
   - Fields: id, name, color, weekday (SmallInteger, 0=Mon…6=Sun), start (Date), end (Date), time_start (Time), time_end (Time), trainer_id
   - Generates Event records for each matching weekday in date range
   - `weekday` is stored explicitly (not derived from datetime)
   - `trainer_id → trainers.id` (FK, SET NULL on delete)

5. **Visits** - QR check-in records
   - PK: composite `(timestamp, uid)`
   - Fields: timestamp (DateTime), uid (string), user_id (nullable FK → users), event_id (nullable FK → events)
   - Both FKs set to SET NULL on delete

6. **UserPaymentHistory** - payment records
   - Fields: id, user_id (FK → users), trainer_id (FK → trainers), payment (Integer), timestamp, comment (nullable)

7. **Intentions** - planned attendance
   - `user_id → users.id`, `event_id → events.id`

### Authentication Flow

**JWT-based OAuth2:**

- Passwords hashed with Argon2 via `pwdlib`
- Login: `POST /api/users/login` → returns `{access_token, token_type: "bearer"}`
- Protected routes use `Depends(oauth2_scheme)` → returns `user_id: int`
- `OAuthPasswordBearer` in `auth.py` verifies token and checks user exists in DB
- Token payload: `{user_id: int, exp: datetime}`
- Config: `SECRET_KEY`, `ALGORITHM = "HS256"`, `ACCESS_TOKEN_EXPIRE_MINUTES = 1440`

### WeeklyEvent Implementation Pattern

WeeklyEvent acts as a template that generates Event instances:

1. **Creation Flow:** generates Events for each matching weekday from `max(start, today)` to `end`
2. **Update Flow:** if date range/time changed → deletes future Events, regenerates; if only name/color/trainer → updates in-place
3. **Delete Flow:** CASCADE deletes future Events (FK with CASCADE), past Events preserved
4. **Sync on startup:** `WeeklyEventService.sync_future_events()` called in lifespan to fill gaps

`weekly_id` FK uses `ondelete="CASCADE"`, so deleting a WeeklyEvent removes its future Events.

### Architecture Patterns

**Layered Architecture:**

1. **Models Layer** (`models/`) - SQLAlchemy 2.0 ORM, `sa.Column` style, all inherit from `Base`
2. **Schemas Layer** (`schemas/`) - Pydantic with `ConfigDict(from_attributes=True)` for ORM compat
3. **Services Layer** (`services/`) - `__init__(self, db: AsyncSession)`, business logic
4. **Routers Layer** (`routers/`) - FastAPI, delegates to services, uses `Depends(db.get_db)` + `Depends(oauth2_scheme)`

**Conventions:**
- Routers use `session` parameter name for AsyncSession
- Services use `self.db` for database operations
- All DB operations async
- SQLAlchemy 2.0 style queries (select/insert/update/delete)
- Bulk inserts: `sa.insert(Model).values(items)`

## Key Conventions

**SQLAlchemy usage:** Core queries only — no ORM relationships (`relationship`), no lazy loading. Queries are written with `select()`, `insert()`, etc. Use `sa.text()` only for PostgreSQL-specific syntax that cannot be expressed via Core. Use `.mappings().all()` for multi-column row results — access by column name, not index. Sessions used as async context managers via `session()` (general use) or `SessionDep` (FastAPI dependency). **Never call `commit()` or `rollback()` or `flush()` manually** — `session()` commits on success and rolls back on exception automatically.

**Model style:** Models are defined with `import sqlalchemy as sa` and classical `sa.Column(...)` — no `Mapped`, no `mapped_column`, no type annotations on columns, no `from __future__ import annotations`, no `__all__`.

**Structured data:** Use Pydantic `BaseModel` for structured objects — no `dataclass`.

**No logic in `__init__.py`:** All logic lives in dedicated modules. `__init__.py` files are re-exports only.

## Frontend Architecture

**React SPA** (Vite + MUI), served from `frontend/dist/` by FastAPI.

- Dev server: `npm run dev` on port 5173, proxies API to backend
- Build: `npm run build` → `frontend/dist/` (FastAPI serves `/assets/` and SPA fallback)
- Auth: JWT stored in context/localStorage, `AuthContext` wraps app
- Routes: `/login`, `/register`, `/` (CalendarPage), `/calendar/:monday`, `/profile`, `/history`
- CORS: FastAPI allows `http://localhost:5173` explicitly

## Security

- Passwords hashed with Argon2 (`pwdlib`)
- JWT tokens, 24h expiry
- `oauth2_scheme` dependency verifies token + checks user exists
