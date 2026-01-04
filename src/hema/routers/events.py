"""API routes for Event management."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hema.db import db
from hema.models.events import EventModel
from hema.models.users import UserModel
from hema.schemas.events import EventResponse

router = APIRouter(prefix="/api/events", tags=["Events"])


@router.get("", response_model=list[EventResponse])
async def list_events(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    session: AsyncSession = Depends(db.get_db),
):
    stmt = (
        select(
            EventModel.id,
            EventModel.name,
            EventModel.color,
            EventModel.start,
            EventModel.end,
            EventModel.weekly_id,
            EventModel.trainer_id,
            UserModel.name.label("trainer_name"),
        )
        .join(UserModel, EventModel.trainer_id == UserModel.id)
        .order_by(EventModel.start, EventModel.id)
        .offset(skip)
        .limit(limit)
    )
    rows = (await session.execute(stmt)).all()

    # Build EventResponse with trainer_name
    events = list(map(EventResponse.model_validate, rows))

    return events


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    session: AsyncSession = Depends(db.get_db),
):
    q = (
        select(
            EventModel.id,
            EventModel.name,
            EventModel.color,
            EventModel.start,
            EventModel.end,
            EventModel.weekly_id,
            EventModel.trainer_id,
            UserModel.name.label("trainer_name"),
        )
        .join(UserModel, EventModel.trainer_id == UserModel.id)
        .where(EventModel.id == event_id)
    )
    row = (await session.execute(q)).fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Event {event_id} not found"
        )

    event_response = EventResponse.model_validate(row)

    return event_response
