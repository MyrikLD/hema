"""API routers for the HEMA training calendar application."""

from hema.routers.calendar import router as calendar_router
from hema.routers.events import router as events_router
from hema.routers.weekly_events import router as weekly_events_router
from hema.routers.users import router as users_router

__all__ = ["calendar_router", "events_router", "weekly_events_router", "users_router"]
