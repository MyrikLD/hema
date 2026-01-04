"""Pydantic schemas for WeeklyEvent (recurring events)."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator, NaiveDatetime


class WeeklyEventBase(BaseModel):
    """Base weekly event schema."""

    model_config = ConfigDict(from_attributes=True)

    start: date  # First date to create events
    end: date  # Last date to create events
    name: str
    color: str = "4CAF50"
    event_start: datetime  # Time for each event (e.g., Monday 18:00)
    event_end: datetime  # Time for each event (e.g., Monday 20:00)
    trainer_id: int

    @field_validator("event_start", "event_end")
    @classmethod
    def remove_timezone(cls, dt) -> datetime:
        return dt.replace(tzinfo=None)


class WeeklyEventCreate(WeeklyEventBase):
    """Schema for creating weekly event."""

    pass


class WeeklyEventUpdate(BaseModel):
    """Schema for updating weekly event."""

    model_config = ConfigDict(from_attributes=True)

    start: date | None = None
    end: date | None = None
    name: str | None = None
    color: str | None = None
    event_start: NaiveDatetime | None = None
    event_end: NaiveDatetime | None = None
    trainer_id: int | None = None

    @field_validator("event_start", "event_end")
    @classmethod
    def remove_timezone(cls, dt) -> datetime | None:
        if dt:
            return dt.replace(tzinfo=None)


class WeeklyEventResponse(WeeklyEventBase):
    """Weekly event response schema with ID."""

    id: int
