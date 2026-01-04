"""Calendar service for building monthly calendar views."""

from calendar import month_name, monthrange
from datetime import date, datetime, timedelta

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from hema.models.events import EventModel
from hema.schemas.calendar import CalendarDay
from hema.schemas.events import EventResponse


class CalendarService:
    """Service for generating calendar data."""

    @staticmethod
    async def get_month_data(db: AsyncSession, year: int, month: int) -> dict:
        """
        Build calendar data structure for template rendering.

        Args:
            db: Database session
            year: Year (e.g., 2026)
            month: Month (1-12)

        Returns:
            Dictionary with calendar data ready for Jinja2 template
        """
        # Validate month
        if not (1 <= month <= 12):
            raise ValueError(f"Invalid month: {month}. Must be 1-12.")

        # Get first and last day of the month
        first_day = date(year, month, 1)
        last_day_num = monthrange(year, month)[1]
        last_day = date(year, month, last_day_num)

        # Calculate calendar grid boundaries (start on Monday)
        # weekday(): Monday=0, Sunday=6
        start_offset = first_day.weekday()  # Days to go back to Monday
        grid_start = first_day - timedelta(days=start_offset)

        # Need 42 cells (6 weeks × 7 days) for consistent grid
        grid_end = grid_start + timedelta(days=41)

        # Query events in the visible range (including adjacent month days)
        q = (
            sa.select(EventModel)
            .where(
                EventModel.start >= datetime.combine(grid_start, datetime.min.time())
            )
            .where(EventModel.start <= datetime.combine(grid_end, datetime.max.time()))
            .order_by(EventModel.start)
        )
        result = await db.execute(q)
        events = result.scalars().all()

        # Group events by date
        events_by_date: dict[date, list[EventResponse]] = {}
        for event in events:
            event_date = event.start.date()
            if event_date not in events_by_date:
                events_by_date[event_date] = []
            events_by_date[event_date].append(EventResponse.model_validate(event))

        # Build 42-day grid
        today = date.today()
        days: list[CalendarDay] = []

        current_date = grid_start
        for _ in range(42):
            days.append(
                CalendarDay(
                    date=current_date,
                    is_today=(current_date == today),
                    is_current_month=(current_date.month == month),
                    events=events_by_date.get(current_date, []),
                )
            )
            current_date += timedelta(days=1)

        # Calculate prev/next month navigation
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1

        if month == 12:
            next_year, next_month = year + 1, 1
        else:
            next_year, next_month = year, month + 1

        # Return data structure for template
        return {
            "year": year,
            "month": month,
            "month_name": month_name[month],
            "days": days,
            "prev_year": prev_year,
            "prev_month": prev_month,
            "next_year": next_year,
            "next_month": next_month,
        }
