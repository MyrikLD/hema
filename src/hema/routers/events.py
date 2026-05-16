"""API routes for Event management."""

from datetime import date

from fastapi import APIRouter, HTTPException, Query, status

from hema.auth import TrainerIdDep
from hema.db import SessionDep
from hema.schemas.events import EventCreateSchema, EventResponse
from hema.services.event import EventService

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", response_model=list[EventResponse])
async def list_events(
    session: SessionDep,
    start: date = Query(default_factory=date.today),
    end: date = Query(default_factory=date.today),
):
    service = EventService(session)
    return await service.list_events(start, end)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    session: SessionDep,
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
    session: SessionDep,
    user_id: TrainerIdDep,
):
    service = EventService(session)

    event = await service.create(event_data, user_id)

    return event


@router.post("/take/{event_id}", response_model=EventResponse)
async def take_event(
    event_id: int,
    session: SessionDep,
    user_id: TrainerIdDep,
):
    service = EventService(session)

    event_response = await service.set_trainer(event_id, user_id)

    return event_response
