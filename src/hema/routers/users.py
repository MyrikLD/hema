from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

from hema.auth import security, require_trainer
from hema.config import settings
from hema.db import db
from hema.schemas.events import EventBase, EventCreate
from hema.schemas.users import (
    UserCreateResponseSchema,
    UserCreateSchema,
    UserProfileUpdateShema,
)
from hema.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

# Configure Jinja2 with templates directory
jinja = Environment(loader=FileSystemLoader(settings.ROOT / "templates"))


@router.post("/registration", response_model=UserCreateResponseSchema)
async def user_registration(
    data: UserCreateSchema,
    session: AsyncSession = Depends(db.get_db),
):
    new_user = await UserService(session).create_user_profile(data)
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with same phone number exists",
        )
    return new_user


@router.get("/", response_model=UserCreateResponseSchema)
async def get_user_profile(
    session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(security),
):
    service = UserService(session)
    user_profile = await service.get_user_profile(user_id=user_id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user_profile


@router.patch("/", response_model=UserCreateResponseSchema)
async def update_user_profile(
    update_data: UserProfileUpdateShema,
    session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(security),
):
    service = UserService(session)
    user_profile = await service.update_user_profile(
        user_id=user_id, update_data=update_data
    )
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user_profile


@router.get("/profile", response_class=HTMLResponse)
async def user_profile_page(
    session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(security),
):
    """Render user profile HTML page"""
    service = UserService(session)
    user_profile = await service.get_user_profile(user_id=user_id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    template = jinja.get_template("user.xhtml")
    return template.render(user=user_profile)


@router.post("/create_event")
async def create_event(
    event_data: EventCreate,
    session: AsyncSession = Depends(db.get_db),
    trainer_id: int = Depends(require_trainer),
):
    """Create a new training event (trainers only)."""
    # Build EventBase with trainer_id from authentication
    event_with_trainer = EventBase(
        name=event_data.name,
        color=event_data.color,
        start=event_data.start,
        end=event_data.end,
        weekly_id=event_data.weekly_id,
        trainer_id=trainer_id
    )
    service = UserService(session)
    event = await service.create_event(event_with_trainer)
    return event


@router.get("/profile/events")
async def get_trainers_events(
    session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(security)
):
    """Get all training events for the authenticated user (trainers only)."""
    service = UserService(session)
    trainers_events = await service.get_trainer_events(user_id=user_id)
    # Return empty list if no events found instead of 404
    return trainers_events if trainers_events else []
