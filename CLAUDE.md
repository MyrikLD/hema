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
# Run development server
python main.py
# or
uvicorn main:api --reload --host 0.0.0.0 --port 8000

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
├── models/              # SQLAlchemy models
│   ├── base.py         # Base declarative class with shared metadata
│   ├── users.py        # UserModel (users)
│   ├── events.py       # EventModel (training sessions)
│   └── visits.py       # VisitModel (attendance records)
└── templates/           # Jinja2 templates for frontend
    └── calendar.xhtml  # Calendar view
```

### Data Model Relationships

**Critical Architecture Detail:** The system has a three-entity model with foreign key relationships:

1. **Users** - users with RFID badges
   - Roles: `user`, `trainer`, `admin`
   - RFID UID links physical badge to user account

2. **Events** - training sessions with assigned trainer
   - `trainer_id` → `Users.id` (FK)
   - Time: `start` and `end` to determine active sessions

3. **Visits** - attendance records (links users and events)
   - `user_id` → `Users.id` (FK)
   - `event_id` → `Events.id` (FK) ⚠️ **NOT IMPLEMENTED in models/visits.py**
   - Created when RFID is scanned during an active training session

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

### Models Pattern

All models inherit from `models.base.Base` (SQLAlchemy DeclarativeBase) with shared `metadata` object for migrations.

**Important:** When adding new fields to models:
- Use SQLAlchemy 2.0 syntax (`sa.Column`)
- Add proper constraints (unique, nullable, default)
- Update relationships for navigation between tables

### Missing Implementation

**TODO Items in current codebase:**

1. **models/visits.py** - missing `event_id` foreign key
2. **models/users.py** - incomplete model (only id), needs:
   - name, email, phone, rfid_uid, role, is_active, created_at
3. **models/events.py** - incomplete, needs:
   - description, max_participants, is_active, created_at
4. **Relationships** - SQLAlchemy relationships not configured between models
5. **config.py** - empty, needs database URL and app settings
6. **Database connection** - SQLAlchemy engine/session not initialized

## API Design Patterns

### Endpoints Structure (to be implemented)

API follows RESTful pattern with resource grouping:
- `/api/auth/*` - authentication
- `/api/users/*` - user CRUD operations
- `/api/events/*` - training sessions CRUD
- `/api/visits/*` - attendance records
- `/api/calendar/{year}/{month}` - calendar data
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

### Calendar View Requirements

- **Monthly view** - main page
- Navigation: left/right arrows to switch months
- Each day cell can contain multiple training sessions
- Click on training → modal with details (trainer, participants, available spots)
- **Responsive design required** - mobile interface for trainers/participants

### Mobile-First Considerations

- Touch-friendly elements (minimum 44x44px for buttons)
- Swipe gestures for month navigation on mobile
- Compact calendar view on small screens
- Fast loading (minimal JS, lazy loading)

## Development Notes

### Database Setup Order

When implementing database:
1. Complete all model definitions first
2. Add all foreign keys and relationships
3. Configure database connection in config.py
4. Initialize Alembic
5. Generate initial migration
6. Apply migration to create tables

### Testing Strategy

Focus on:
- Model validation and constraints
- RFID check-in logic (critical business logic)
- Calendar data generation (edge cases: month boundaries, recurring events)
- API endpoint security (auth required for admin operations)

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

- Store RFID UIDs as-is (don't encrypt in DB, but protect at API level)
- JWT for web authentication
- RFID endpoint must be rate-limited (protection from brute-force scanning)
- Admin endpoints require authentication with `admin` or `trainer` role
- Validate all user inputs via Pydantic schemas

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
