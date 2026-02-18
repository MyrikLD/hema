"""API routers for the HEMA training calendar application."""

from fastapi import APIRouter

from .calendar import router as calendar_router
from .esp import router as esp_router
from .events import router as events_router
from .intentions import router as intentions_router
from .users import router as users_router
from .visits import router as visits_router
from .weekly_events import router as weekly_events_router
from .payments import router as payment_router

api_router = APIRouter(prefix="/api")
api_router.include_router(calendar_router)
api_router.include_router(events_router)
api_router.include_router(weekly_events_router)
api_router.include_router(users_router)
api_router.include_router(esp_router)
api_router.include_router(intentions_router)
api_router.include_router(visits_router)
api_router.include_router(payment_router)
__all__ = ["api_router"]
