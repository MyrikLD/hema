"""Pydantic schemas for Event API models."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EventBase(BaseModel):
    """Base event schema with common fields."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    color: str = "4CAF50"
    start: datetime
    end: datetime
    weekly_id: int | None = None
    trainer_id: int


class EventCreate(BaseModel):
    """Event creation schema without trainer_id (comes from auth)."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    color: str = "4CAF50"
    start: datetime
    end: datetime
    weekly_id: int | None = None


class EventResponse(EventBase):
    """Event response schema with ID and optional trainer name."""

    id: int
    trainer_name: str
