# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HEMA Training Calendar - training attendance tracking system for Historical European Martial Arts with automatic RFID badge check-in.

**Tech Stack:** FastAPI + PostgreSQL + SQLAlchemy + ESP32/MicroPython for RFID

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

# Health check
curl http://localhost:8000/health

# Access calendar (requires HTTP Basic Auth)
# Browser will prompt for username/password
open http://localhost:8000/calendar
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

# Format specific files
black main.py models/
```

### Database Operations
```bash
# Database migrations will use Alembic (to be configured)
# alembic revision --autogenerate -m "description"
# alembic upgrade head
# alembic downgrade -1
```

## Code Architecture

### Application Structure

```
hema/
├── main.py              # FastAPI application entry point
├── config.py            # Pydantic settings (database, app config)
├── auth.py              # HTTP Basic Auth implementation
├── db.py                # Database connection and session management
├── models/              # SQLAlchemy models
│   ├── base.py         # Base declarative class with shared metadata
│   ├── users.py        # UserModel (users)
│   ├── events.py       # EventModel (training sessions)
│   ├── visits.py       # VisitModel (attendance records)
│   ├── intentions.py   # IntentionModel (planned attendance)
│   └── weekly_events.py # WeeklyEventModel (recurring event templates)
├── schemas/             # Pydantic schemas for API validation
│   ├── events.py       # EventBase, EventResponse
│   ├── calendar.py     # CalendarDay, CalendarMonth
│   └── weekly_events.py # WeeklyEventCreate, WeeklyEventUpdate, WeeklyEventResponse
├── routers/             # API route handlers
│   ├── calendar.py     # Calendar view routes
│   ├── events.py       # Event CRUD endpoints
│   └── weekly_events.py # WeeklyEvent CRUD endpoints
├── services/            # Business logic layer
│   ├── calendar_service.py # Calendar data generation
│   └── weekly_event_service.py # Recurring event management
└── templates/           # Jinja2 templates for frontend
    └── calendar.xhtml  # Monthly calendar view (responsive)
```

### Data Model Relationships

**Critical Architecture Detail:** The system uses the following data model:

1. **Users** - users with RFID badges
   - Fields: id, name, password, rfid_uid, role, is_active, created_at
   - Roles: `user`, `trainer`, `admin`
   - RFID UID links physical badge to user account

2. **Events** - individual training sessions
   - Fields: id, name, color (6-char hex), start, end, trainer_id, weekly_id
   - `trainer_id` → `Users.id` (FK) - assigned trainer
   - `weekly_id` → `WeeklyEvents.id` (FK, nullable) - link to recurring event template
   - Color stored as 6-character hex (e.g., "4CAF50")

3. **WeeklyEvents** - recurring event templates (trainer abstraction)
   - Fields: id, name, color, start (date), end (date), event_start (datetime), event_end (datetime), trainer_id
   - Generates Event records for each matching weekday in date range
   - Weekday determined from `event_start.weekday()`
   - When created: generates Events for all matching dates
   - When updated (date range): deletes future Events and regenerates
   - When deleted: sets `weekly_id=NULL` for future Events (doesn't cascade delete)

4. **Visits** - attendance records (links users and events)
   - `user_id` → `Users.id` (FK)
   - `event_id` → `Events.id` (FK) - ⚠️ **May be NULL during RFID scan**
   - Created when RFID is scanned; event association computed post-processing

5. **Intentions** - planned attendance (user declares intent to attend)
   - `user_id` → `Users.id` (FK)
   - `event_id` → `Events.id` (FK)

### RFID Check-in Flow

**Critical Business Logic (Updated Architecture):**

```
1. ESP32 scans RFID → sends {"rfid_uid": "...", "timestamp": "..."}
2. Backend saves Visit(user_id, timestamp) - NO event_id during scan
3. Post-processing: Find event by matching timestamp with event.start/end range
4. Returns success/error for ESP32 indication (LED/buzzer)
```

**Design Decision:** RFID scanning saves timestamp only, allowing:
- Duplicates (multiple badge scans tracked separately)
- Event association computed later (not during scan)
- Simpler ESP32 logic (no event lookup required)

### Architecture Patterns

**Layered Architecture:**

1. **Models Layer** (`models/`)
   - SQLAlchemy ORM models
   - All inherit from `models.base.Base` (DeclarativeBase)
   - Shared `metadata` object for Alembic migrations
   - Use SQLAlchemy 2.0 syntax (`sa.Column`)

2. **Schemas Layer** (`schemas/`)
   - Pydantic models for validation
   - Use `ConfigDict(from_attributes=True)` for ORM compatibility
   - Separate schemas for Create/Update/Response operations
   - Example: EventBase → EventResponse (adds id, trainer_name)

3. **Services Layer** (`services/`)
   - Business logic encapsulation
   - Database queries and data transformations
   - Instance methods with `__init__(self, db: AsyncSession)` pattern
   - Return dicts or ORM objects depending on use case

4. **Routers Layer** (`routers/`)
   - FastAPI route handlers
   - Dependency injection: `Depends(db.get_db)`, `Depends(security)`
   - Minimal logic - delegates to Services
   - Response models via Pydantic schemas

**Conventions:**
- Routers use `session` parameter name for AsyncSession
- Services use `self.db` for database operations
- All database operations are async (`await`)
- SQL queries use SQLAlchemy 2.0 style (select, insert, update, delete)
- Bulk operations prefer `sa.insert().values(items)` over ORM loops

### WeeklyEvent Implementation Pattern

**Recurring Events System:**

WeeklyEvent acts as a template that generates multiple Event instances:

1. **Creation Flow:**
   - Trainer creates WeeklyEvent with date range (start, end) and time template (event_start, event_end)
   - System extracts weekday from `event_start.weekday()` (0=Monday, 6=Sunday)
   - Generates Event for each matching weekday in range
   - Events only created from `max(start, today)` onwards (skips past dates)
   - Each Event gets `weekly_id` pointing to WeeklyEvent template

2. **Update Flow:**
   - If `start/end/event_start` changed → deletes future Events, regenerates new ones
   - If only `name/color/trainer_id` changed → updates all future Events in-place
   - Past Events never modified (preserves history)

3. **Delete Flow:**
   - Sets `weekly_id=NULL` for all future Events (unlinks but preserves)
   - Deletes WeeklyEvent record
   - Past Events remain untouched

4. **Implementation Details:**
   - WeeklyEventService uses instance methods (initialized with `db: AsyncSession`)
   - Bulk inserts via `sa.insert(EventModel).values(items)` for performance
   - Returns dicts instead of ORM objects for faster serialization
   - Only operates on future Events (`EventModel.start > datetime.now()`)

### Implemented Features

**✅ Completed:**

1. **Authentication** - HTTP Basic Auth (username/password)
   - `HTTPBasicAuth` class in `auth.py`
   - Logout via credential clearing

2. **Calendar System** - Monthly calendar view
   - 42-day grid (6 weeks × 7 days)
   - Responsive design (mobile-first CSS Grid)
   - Navigation: prev/next month, click title to return to current month
   - Events displayed with custom colors
   - Modal for event details

3. **Event Management**
   - GET `/api/events` - List events with pagination
   - GET `/api/events/{id}` - Get single event
   - EventResponse includes `trainer_name` via SQL JOIN

4. **WeeklyEvent System** (Recurring Events)
   - Full CRUD: POST/GET/PUT/DELETE `/api/weekly`
   - Automatic Event generation for matching weekdays
   - Smart updates: regenerates Events when date range changes
   - Only future Events updated/deleted (preserves history)

5. **Pydantic Schemas** - Full validation layer
   - EventBase, EventResponse
   - CalendarDay, CalendarMonth
   - WeeklyEventCreate, WeeklyEventUpdate, WeeklyEventResponse

6. **Services Layer**
   - `CalendarService.get_month_data()` - Calendar data generation
   - `WeeklyEventService` - Recurring event management

### Missing Implementation

**⚠️ TODO Items:**

1. **RFID Check-in Endpoint** - `POST /api/checkin` not yet implemented
2. **Visits Management** - No API endpoints for attendance records
3. **User Management** - No CRUD endpoints for users
4. **Intentions** - No API for planned attendance
5. **Event Details Modal** - JavaScript for event modal not implemented
6. **Admin UI** - No separate trainer/admin interface for WeeklyEvents

## API Design Patterns

### Implemented Endpoints

API follows RESTful pattern with resource grouping:

**Calendar Views (HTML):**
- `GET /calendar` - Current month calendar (requires HTTP Basic Auth)
- `GET /calendar/{year}/{month}` - Specific month calendar

**Events API (JSON):**
- `GET /api/events` - List all events (with pagination: skip, limit)
- `GET /api/events/{id}` - Get single event details

**WeeklyEvents API (JSON, Trainer-only):**
- `GET /api/weekly` - List recurring event templates
- `GET /api/weekly/{id}` - Get single template
- `POST /api/weekly` - Create recurring event (generates Events)
- `PUT /api/weekly/{id}` - Update template (regenerates future Events if needed)
- `DELETE /api/weekly/{id}` - Delete template (preserves past Events)

### TODO Endpoints

- `/api/auth/*` - authentication (currently using HTTP Basic Auth)
- `/api/users/*` - user CRUD operations
- `/api/visits/*` - attendance records
- `/api/intentions/*` - planned attendance
- `/api/checkin` - **special endpoint for ESP32**

### RFID Endpoint Requirements

`POST /api/checkin` must:
- Accept minimal payload from ESP32 (IoT device with limited resources)
- Respond quickly (ESP32 timeout ~5-10 seconds)
- Return simple JSON: `{"success": true/false, "message": "..."}`
- Handle edge cases:
  - RFID UID not found in database
  - No active training session at the moment
  - Duplicate registration (already checked in to this session)

## Frontend Architecture

**Server-Side Rendering** with Jinja2 for main pages, minimal JavaScript for interactivity.

### Calendar View (Implemented)

**Features:**
- **Monthly view** - 42-day grid (6 weeks × 7 days)
- Navigation: left/right arrows to switch months
- Click month title to return to current month
- Each day cell can contain multiple training sessions
- Events displayed with custom colors (6-character hex)
- Logout button in header (clears HTTP Basic Auth credentials)

**Responsive Design:**
- CSS Grid layout (7 columns for desktop)
- Mobile-first approach: stacks to single column on small screens
- Touch-friendly elements (44x44px minimum tap targets)
- Month name generated client-side via JavaScript
- Events show: time, name, trainer name

**TODO:**
- Click on training → modal with details (trainer, participants, available spots)
- Swipe gestures for month navigation on mobile

## Development Notes

### Database Setup Order

When implementing database:
1. Complete all model definitions first
2. Add all foreign keys and relationships
3. Configure database connection in config.py
4. Initialize Alembic
5. Generate initial migration
6. Apply migration to create tables

### Event Color System

Events use 6-character hex colors for visual distinction:

- Stored in database as `String(6)` (e.g., "4CAF50")
- Default color: "4CAF50" (Material Design Green)
- Rendered in template: `style="background-color: #{{ event.color }}"`
- Colors inherited from WeeklyEvent template to generated Events
- Hover effect: `filter: brightness(0.9)` for better UX

**Usage:**
- Different colors for different training types (Longsword, Rapier, etc.)
- Color-code by trainer for quick visual identification
- Frontend displays events with inline styles for maximum compatibility

### ESP32 Integration

MicroPython code for ESP32 is outside this repository, but the API must consider:
- Minimal response size (limited memory on ESP32)
- Network error handling (WiFi may disconnect)
- Retry logic should be on ESP32 side
- Use HTTP (not HTTPS) for simplicity or self-signed certificate

## Configuration

### Environment Variables (to be added to config.py)

```python
DATABASE_URL: str  # postgresql+asyncpg://user:pass@host/db
SECRET_KEY: str    # for JWT tokens
DEBUG: bool = False
CORS_ORIGINS: list[str] = ["*"]
RFID_CHECKIN_WINDOW: int = 15  # minutes before/after start for check-in
```

## Security Considerations

**Current Implementation:**
- HTTP Basic Auth for web interface (username + password)
- Passwords stored in plaintext (⚠️ TODO: hash with bcrypt/argon2)
- Calendar requires authentication via `Depends(security)`
- Logout via credential clearing (redirects to invalid auth URL)

**TODO:**
- Hash passwords before storing in database
- JWT tokens for API authentication (optional, HTTP Basic Auth works for now)
- RFID endpoint must be rate-limited (protection from brute-force scanning)
- Role-based access control: WeeklyEvents API restricted to trainers
- Store RFID UIDs as-is (don't encrypt in DB, but protect at API level)
- Validate all user inputs via Pydantic schemas (✅ implemented)

## Performance Optimization

- Indexes on: `users.rfid_uid`, `events.start`, `events.end`, `visits.user_id`, `visits.event_id`
- Cache calendar queries (Redis in the future)
- Use async/await for database queries
- Pagination for user and visit lists

## Deployment (future)

Project is being prepared for Docker deployment:
- PostgreSQL container
- FastAPI application container
- Reverse proxy (nginx) for HTTPS and static files
- ESP32 connects to public API endpoint
