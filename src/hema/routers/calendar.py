from datetime import date

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from hema.auth import oauth2_scheme
from hema.db import db
from hema.schemas.calendar import CalendarMonth
from hema.services.calendar_service import CalendarService

router = APIRouter(tags=["Calendar"])


@router.get("/calendar", response_model=CalendarMonth)
async def calendar_current_json(
    db_session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(oauth2_scheme),
):
    today = date.today()
    return await CalendarService.get_month_data(db_session, today)


@router.get("/calendar/{year}/{month}", response_model=CalendarMonth)
async def calendar_month_json(
    year: int = Path(gt=2024, le=2100),
    month: int = Path(ge=1, le=12),
    db_session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(oauth2_scheme),
):
    month_date = date(year, month, 1)
    return await CalendarService.get_month_data(db_session, month_date)
