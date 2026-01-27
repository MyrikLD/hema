"""API routes for WeeklyEvent (recurring events) management."""

from datetime import date, datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from hema.auth import oauth2_scheme
from hema.db import db
from hema.schemas.weekly_events import (
    WeeklyEventCreate,
    WeeklyEventResponse,
    WeeklyEventUpdate,
)
from hema.services.weekly_event_service import WeeklyEventService

router = APIRouter(prefix="/api/weekly", tags=["Weekly Events"])


@router.get("", response_model=list[WeeklyEventResponse])
async def list_weekly_events(
    start: datetime = Query(default_factory=lambda: datetime.combine(date.today(), time.min)),
    end: datetime = Query(default_factory=lambda: datetime.combine(date.today(), time.max)),
    session: AsyncSession = Depends(db.get_db),
):
    weekly_events = await WeeklyEventService(session).list_weekly_events(start, end)

    # Convert to response schema
    responses = []
    for we in weekly_events:
        responses.append(WeeklyEventResponse.model_validate(we))

    return responses


@router.get("/{weekly_event_id}", response_model=WeeklyEventResponse)
async def get_weekly_event(
    weekly_event_id: int,
    session: AsyncSession = Depends(db.get_db),
):
    weekly_event = await WeeklyEventService(session).get_weekly_event(weekly_event_id)

    if not weekly_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"WeeklyEvent {weekly_event_id} not found",
        )

    return weekly_event


@router.post("", response_model=WeeklyEventResponse, status_code=status.HTTP_201_CREATED)
async def create_weekly_event(
    data: WeeklyEventCreate,
    session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(oauth2_scheme),
):
    weekly_event = await WeeklyEventService(session).create_weekly_event(data, user_id)

    return weekly_event


@router.put("/{weekly_event_id}", response_model=WeeklyEventResponse)
async def update_weekly_event(
    weekly_event_id: int,
    data: WeeklyEventUpdate,
    session: AsyncSession = Depends(db.get_db),
):
    weekly_event = await WeeklyEventService(session).update_weekly_event(weekly_event_id, data)

    if not weekly_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"WeeklyEvent {weekly_event_id} not found",
        )

    return weekly_event


@router.delete("/{weekly_event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weekly_event(
    weekly_event_id: int,
    session: AsyncSession = Depends(db.get_db),
):
    deleted = await WeeklyEventService(session).delete_weekly_event(weekly_event_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"WeeklyEvent {weekly_event_id} not found",
        )
