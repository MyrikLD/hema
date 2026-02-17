"""API routers for the HEMA training calendar application."""

from .calendar import router as calendar_router
from .esp import router as esp_router
from .events import router as events_router
from .users import router as users_router
from .weekly_events import router as weekly_events_router
from .payments import router as payment_router

__all__ = [
    "calendar_router",
    "events_router",
    "weekly_events_router",
    "users_router",
    "esp_router",
    "payment_router",
]
