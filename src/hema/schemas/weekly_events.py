"""Pydantic schemas for WeeklyEvent (recurring events)."""

from datetime import date, datetime, UTC

from pydantic import BaseModel, ConfigDict, field_validator, model_validator, NaiveDatetime


class WeeklyEventBase(BaseModel):
    """Base weekly event schema."""

    model_config = ConfigDict(from_attributes=True)

    start: date  # First date to create events
    end: date  # Last date to create events
    name: str
    color: str = "4CAF50"
    event_start: datetime  # Time for each event (e.g., Monday 18:00)
    event_end: datetime  # Time for each event (e.g., Monday 20:00)

    @model_validator(mode="after")
    def validate_start_end(cls, values):
        if values.start > values.end:
            raise ValueError("start must be before end")
        if values.event_start > values.event_end:
            raise ValueError("event_start must be before event_end")
        return values

    @field_validator("event_start", "event_end", mode="after")
    def validate_date(cls, value):
        return value.astimezone(UTC).replace(tzinfo=None)


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

    @field_validator("start", "end", "event_start", "event_end", mode="after")
    def validate_date(cls, value):
        if value:
            return value.astimezone(UTC).replace(tzinfo=None)


class WeeklyEventResponse(WeeklyEventBase):
    """Weekly event response schema with ID."""

    id: int
    trainer_id: int
