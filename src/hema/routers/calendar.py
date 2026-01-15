from datetime import date

from fastapi import APIRouter, Depends, Path
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

from hema.auth import security
from hema.config import settings
from hema.db import db
from hema.services.calendar_service import CalendarService
from hema.schemas.calendar import CalendarMonth

# HTML router
router = APIRouter(prefix="/calendar", tags=["Calendar"])

# JSON API router (без вложенного префикса)
api_router = APIRouter(prefix="/api/calendar", tags=["Calendar API"])

# Configure Jinja2 with templates directory
jinja = Environment(loader=FileSystemLoader(settings.ROOT / "templates"))


@router.get("/", response_class=HTMLResponse)
async def calendar_current(
    db_session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(security),
):
    today = date.today()
    calendar_data = await CalendarService.get_month_data(db_session, today)
    template = jinja.get_template("calendar.xhtml")
    return template.render(**calendar_data.model_dump())


@router.get("/{year}/{month}", response_class=HTMLResponse)
async def calendar_month(
    year: int = Path(gt=2024, le=2100),
    month: int = Path(ge=1, le=12),
    db_session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(security),
):
    month_date = date(year, month, 1)
    calendar_data = await CalendarService.get_month_data(db_session, month_date)
    template = jinja.get_template("calendar.xhtml")
    return template.render(**calendar_data.model_dump())


# JSON API endpoints for Next.js frontend
@api_router.get("/", response_model=CalendarMonth)
async def api_calendar_current(
    db_session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(security),
):
    today = date.today()
    return await CalendarService.get_month_data(db_session, today)


@api_router.get("/{year}/{month}", response_model=CalendarMonth)
async def api_calendar_month(
    year: int = Path(gt=2024, le=2100),
    month: int = Path(ge=1, le=12),
    db_session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(security),
):
    month_date = date(year, month, 1)
    return await CalendarService.get_month_data(db_session, month_date)


