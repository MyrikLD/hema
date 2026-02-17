from datetime import date

from fastapi import APIRouter, Depends, Path
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

from hema.auth import oauth2_scheme
from hema.config import settings
from hema.db import db
from hema.schemas.calendar import CalendarMonth
from hema.services.calendar_service import CalendarService

router = APIRouter(tags=["Calendar"])


# Configure Jinja2 with templates directory
jinja = Environment(loader=FileSystemLoader(settings.ROOT / "templates"))


# --- HTML endpoints (legacy Jinja2 calendar) ---


@router.get("/calendar/", response_class=HTMLResponse)
async def calendar_current_html(
    db_session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(oauth2_scheme),
):
    today = date.today()
    calendar_data = await CalendarService.get_month_data(db_session, today)
    template = jinja.get_template("calendar.xhtml")
    return template.render(**calendar_data.model_dump())


@router.get("/calendar/{year}/{month}", response_class=HTMLResponse)
async def calendar_month_html(
    year: int = Path(gt=2024, le=2100),
    month: int = Path(ge=1, le=12),
    db_session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(oauth2_scheme),
):
    month_date = date(year, month, 1)
    calendar_data = await CalendarService.get_month_data(db_session, month_date)
    template = jinja.get_template("calendar.xhtml")
    return template.render(**calendar_data.model_dump())


# --- JSON API endpoints (for React SPA) ---


@router.get("/api/calendar", response_model=CalendarMonth)
async def calendar_current_json(
    db_session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(oauth2_scheme),
):
    today = date.today()
    return await CalendarService.get_month_data(db_session, today)


@router.get("/api/calendar/{year}/{month}", response_model=CalendarMonth)
async def calendar_month_json(
    year: int = Path(gt=2024, le=2100),
    month: int = Path(ge=1, le=12),
    db_session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(oauth2_scheme),
):
    month_date = date(year, month, 1)
    return await CalendarService.get_month_data(db_session, month_date)
