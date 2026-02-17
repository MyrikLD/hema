from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from hema.auth import oauth2_scheme
from hema.db import db
from hema.schemas.intentions import IntentionCreate, IntentionResponse
from hema.services.intention_service import IntentionService

router = APIRouter(prefix="/api/intentions", tags=["Intentions"])


@router.post("", response_model=IntentionResponse, status_code=status.HTTP_201_CREATED)
async def create_intention(
    data: IntentionCreate,
    session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(oauth2_scheme),
):
    service = IntentionService(session)
    result = await service.create(user_id, data.event_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already signed up for this event",
        )
    return result


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_intention(
    event_id: int,
    session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(oauth2_scheme),
):
    service = IntentionService(session)
    deleted = await service.delete(user_id, event_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intention not found",
        )


@router.get("/event/{event_id}")
async def get_event_attendees(
    event_id: int,
    session: AsyncSession = Depends(db.get_db),
):
    service = IntentionService(session)
    return await service.get_for_event(event_id)


@router.get("/me/{event_id}")
async def check_my_intention(
    event_id: int,
    session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(oauth2_scheme),
):
    service = IntentionService(session)
    return {"has_intention": await service.has_intention(user_id, event_id)}
