"""Pydantic schemas for Event API models."""

from datetime import datetime, UTC

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class EventBase(BaseModel):
    """Base event schema with common fields."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    color: str = "4CAF50"
    start: datetime
    end: datetime
    weekly_id: int | None = None
    trainer_id: int | None
    price: int | None

    @field_validator("start", "end", mode="before")
    def validate_date(cls, value):
        return value.astimezone(UTC).replace(tzinfo=None)


class EventResponse(EventBase):
    """Event response schema with ID and optional trainer name."""

    id: int


class EventCreateSchema(BaseModel):
    """Event create schema."""

    name: str
    color: str = "4CAF50"
    start: datetime
    end: datetime
    price: int | None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_start_end(cls, values):
        if values.start > values.end:
            raise ValueError("start must be before end")
        return values

    @field_validator("start", "end", mode="after")
    def validate_date(cls, value):
        return value.astimezone(UTC).replace(tzinfo=None)
