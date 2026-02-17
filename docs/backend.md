# Backend Notes

## Stack
- FastAPI (async)
- SQLAlchemy 2.0 (async, `asyncpg`)
- PostgreSQL
- Alembic for migrations
- Pydantic v2 for schemas

## Models
- `UserModel` — id, name, password (Argon2), rfid_uid, role (user/trainer/admin), is_active
- `EventModel` — id, name, color (6-char hex), start, end, trainer_id (FK), weekly_id (FK nullable)
- `WeeklyEventModel` — recurring template, generates Events for matching weekdays
- `VisitModel` — user_id (FK), event_id (FK, nullable), timestamp
- `IntentionModel` — user_id (FK), event_id (FK)

## Auth
- JWT tokens (was HTTP Basic Auth, migrated)
- Argon2 password hashing (`Argon2Hasher`)
- Routes: `/api/auth/login`, `/api/auth/register`, `/api/auth/me`

## Routers
- `/api/events` — event list, detail
- `/api/weekly` — recurring events CRUD (trainer-only)
- `/calendar` / `/calendar/{year}/{month}` — calendar data (JSON)
- `/api/users` — user management
- `/api/intentions` — sign up / cancel for events
- `/api/visits` — attendance records
- `/health` — health check

## Services Pattern
```python
class SomeService:
    def __init__(self, db: AsyncSession):
        self.db = db
    async def method(self, ...):
        ...
```

## Conventions
- `session` param name in routers for AsyncSession
- SQLAlchemy 2.0 style: `select()`, `insert()`, etc.
- Bulk ops: `sa.insert(Model).values(items)`
- Schemas: separate Create/Update/Response models, `ConfigDict(from_attributes=True)`
- Color: 6-char hex without `#`, default "4CAF50"

## Database
- Migrations: `alembic revision --autogenerate` → `alembic upgrade head`

