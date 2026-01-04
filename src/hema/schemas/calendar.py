"""Pydantic schemas for Calendar data structures."""

from datetime import date

from pydantic import BaseModel

from hema.schemas.events import EventResponse


class CalendarDay(BaseModel):
    """Single day in the calendar grid."""

    date: date
    is_today: bool
    is_current_month: bool
    events: list[EventResponse]


class CalendarMonth(BaseModel):
    """Complete calendar month data for template rendering."""

    date: date
    days: list[CalendarDay]
    prev_date: date
    next_date: date
