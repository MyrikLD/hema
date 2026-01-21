"""API routes for Event management."""

from datetime import date, datetime, time, UTC

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from hema.auth import security, oauth2_scheme
from hema.db import db
from hema.schemas.events import EventCreateSchema, EventResponse
from hema.services.event import EventService

router = APIRouter(prefix="/api/events", tags=["Events"])


@router.get("", response_model=list[EventResponse])
async def list_events(
    start: datetime = Query(default_factory=lambda: datetime.combine(date.today(), time.min)),
    end: datetime = Query(default_factory=lambda: datetime.combine(date.today(), time.max)),
    session: AsyncSession = Depends(db.get_db),
):
    service = EventService(session)
    events = await service.list_events(
        start.astimezone(UTC).replace(tzinfo=None),
        end.astimezone(UTC).replace(tzinfo=None),
    )

    return events


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    session: AsyncSession = Depends(db.get_db),
):
    service = EventService(session)
    event_response = await service.by_id(event_id)

    if not event_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Event {event_id} not found"
        )

    return event_response


@router.post("", response_model=EventResponse)
async def create_event(
    event_data: EventCreateSchema,
    session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(oauth2_scheme),
):
    service = EventService(session)

    event_response = await service.create(event_data, user_id)

    return event_response


@router.post("/take/{event_id}", response_model=EventResponse)
async def create_event(
    event_id: int,
    session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(oauth2_scheme),
):
    service = EventService(session)

    event_response = await service.set_trainer(event_id, user_id)

    return event_response
