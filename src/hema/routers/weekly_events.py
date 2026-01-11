"""API routes for WeeklyEvent (recurring events) management."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from hema.db import db
from hema.schemas.weekly_events import (
    WeeklyEventCreate,
    WeeklyEventResponse,
    WeeklyEventUpdate,
)
from hema.services.weekly_event_service import WeeklyEventService
from hema.auth import require_trainer

router = APIRouter(prefix="/api/weekly", tags=["Weekly Events"])


@router.get("", response_model=list[WeeklyEventResponse])
async def list_weekly_events(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    session: AsyncSession = Depends(db.get_db),
):
    weekly_events = await WeeklyEventService(session).list_weekly_events(skip, limit)

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


@router.post(
    "", response_model=WeeklyEventResponse, status_code=status.HTTP_201_CREATED
)
async def create_weekly_event(
    data: WeeklyEventCreate,
    session: AsyncSession = Depends(db.get_db),
    trainer_id: int = Depends(require_trainer),
):
    weekly_event = await WeeklyEventService(session).create_weekly_event(data)

    return weekly_event


@router.put("/{weekly_event_id}", response_model=WeeklyEventResponse)
async def update_weekly_event(
    weekly_event_id: int,
    data: WeeklyEventUpdate,
    session: AsyncSession = Depends(db.get_db),
):
    weekly_event = await WeeklyEventService(session).update_weekly_event(
        weekly_event_id, data
    )

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
