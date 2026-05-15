from datetime import date

import sqlalchemy as sa
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from hema.db import db
from hema.models.users import UserModel
from hema.models.weekly_events import WeeklyEventModel
from hema.schemas.schedule import ScheduleEntry

router = APIRouter(prefix="/schedule", tags=["Schedule"])


@router.get("", response_model=list[ScheduleEntry])
async def get_schedule(
    start: date = Query(default_factory=date.today),
    end: date = Query(default_factory=date.today),
    session: AsyncSession = Depends(db.get_db),
):
    q = (
        sa.select(
            *WeeklyEventModel.__table__.c,
            UserModel.name.label("trainer_name"),
        )
        .outerjoin(UserModel, WeeklyEventModel.trainer_id == UserModel.id)
        .where(WeeklyEventModel.start <= end)
        .where(WeeklyEventModel.end >= start)
        .order_by(WeeklyEventModel.weekday, WeeklyEventModel.time_start)
    )
    rows = (await session.execute(q)).mappings().all()
    return [ScheduleEntry.model_validate(row) for row in rows]
