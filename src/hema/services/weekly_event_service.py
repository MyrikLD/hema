"""Service for managing WeeklyEvent (recurring events) and generating Event instances."""

from datetime import date, datetime, timedelta

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from hema.models.events import EventModel
from hema.models.weekly_events import WeeklyEventModel
from hema.schemas.weekly_events import WeeklyEventCreate, WeeklyEventUpdate


class WeeklyEventService:
    """Service for managing recurring weekly events."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_events(
        self,
        name: str,
        color: str,
        event_start: datetime,
        event_end: datetime,
        start: date,
        end: date,
        weekly_event_id: int,
        trainer_id: int,
    ) -> int:
        # Extract target weekday from event_start (0=Monday, 6=Sunday)
        target_weekday = event_start.weekday()

        # Extract time components from event_start and event_end
        start_time = event_start.time()
        end_time = event_end.time()

        # Find all dates in range matching the target weekday
        current_date = max(start, datetime.now().date())

        items = []

        while current_date <= end:
            if current_date.weekday() == target_weekday:
                # Combine date + time to create event datetime
                # Create Event instance
                items.append(
                    {
                        EventModel.name: name,
                        EventModel.color: color,
                        EventModel.start: datetime.combine(current_date, start_time),
                        EventModel.end: datetime.combine(current_date, end_time),
                        EventModel.weekly_id: weekly_event_id,
                        EventModel.trainer_id: trainer_id,
                    }
                )

            current_date += timedelta(days=1)

        await self.db.execute(sa.insert(EventModel).values(items))

        return len(items)

    async def create_weekly_event(self, data: WeeklyEventCreate) -> dict:
        # Create WeeklyEvent record
        weekly_event_id = await self.db.scalar(
            sa.insert(WeeklyEventModel)
            .values(
                {
                    WeeklyEventModel.start: data.start,
                    WeeklyEventModel.end: data.end,
                    WeeklyEventModel.name: data.name,
                    WeeklyEventModel.color: data.color,
                    WeeklyEventModel.event_start: data.event_start,
                    WeeklyEventModel.event_end: data.event_end,
                    WeeklyEventModel.trainer_id: data.trainer_id,
                }
            )
            .returning(WeeklyEventModel.id)
        )

        # Generate Event instances
        await self.generate_events(
            name=data.name,
            color=data.color,
            event_start=data.event_start,
            event_end=data.event_end,
            start=data.start,
            end=data.end,
            trainer_id=data.trainer_id,
            weekly_event_id=weekly_event_id,
        )

        return await self.get_weekly_event(weekly_event_id)

    async def update_weekly_event(
        self, weekly_event_id: int, data: WeeklyEventUpdate
    ) -> dict | None:
        # Fetch WeeklyEvent
        q = sa.select(*WeeklyEventModel.__table__.c).where(
            WeeklyEventModel.id == weekly_event_id
        )
        weekly_event: dict = (await self.db.execute(q)).mappings().fetchone()

        if not weekly_event:
            return None

        _data = data.model_dump(exclude_unset=True)

        # Track if date range changed (requires regeneration)
        date_range_changed = False
        if _data["start"] is not None and _data["start"] != weekly_event["start"]:
            date_range_changed = True
        if _data["end"] is not None and _data["end"] != weekly_event["end"]:
            date_range_changed = True
        if (
            _data["event_start"] is not None
            and _data["event_start"] != weekly_event["event_start"]
        ):
            date_range_changed = True  # Weekday might change

        # Update other fields
        q = (
            sa.update(WeeklyEventModel)
            .where(WeeklyEventModel.id == weekly_event_id)
            .values(_data)
        )
        await self.db.execute(q)

        if date_range_changed:
            # Delete all old events
            q = sa.delete(EventModel).where(
                EventModel.weekly_id == weekly_event_id,
                EventModel.start > datetime.now(),
            )
            await self.db.execute(q)

            # Regenerate events
            await self.generate_events(
                name=weekly_event["name"],
                color=weekly_event["color"],
                event_start=weekly_event["event_start"],
                event_end=weekly_event["event_end"],
                start=weekly_event["start"],
                end=weekly_event["end"],
                trainer_id=weekly_event["trainer_id"],
                weekly_event_id=weekly_event_id,
            )
        else:
            # Update all existing events with new values
            q = (
                sa.update(EventModel)
                .where(
                    EventModel.weekly_id == weekly_event_id,
                    EventModel.start > datetime.now(),
                )
                .values(
                    name=weekly_event["name"],
                    color=weekly_event["color"],
                    trainer_id=weekly_event["trainer_id"],
                )
            )
            await self.db.execute(q)

        return weekly_event

    async def delete_weekly_event(self, weekly_event_id: int) -> bool:
        q = (
            sa.update(EventModel)
            .where(
                EventModel.weekly_id == weekly_event_id,
                EventModel.start > datetime.now(),
            )
            .values({EventModel.weekly_id: None})
        )
        await self.db.execute(q)

        q = sa.delete(WeeklyEventModel).where(
            WeeklyEventModel.id == weekly_event_id,
            EventModel.start > datetime.now(),
        )

        result = await self.db.execute(q)

        return result.rowcount > 0

    async def get_weekly_event(self, weekly_event_id: int) -> dict | None:
        q = sa.select(*WeeklyEventModel.__table__.c).where(
            WeeklyEventModel.id == weekly_event_id
        )
        d = (await self.db.execute(q)).mappings().fetchone()
        return d

    async def list_weekly_events(
        self, skip: int = 0, limit: int = 100
    ) -> list[WeeklyEventModel]:
        q = (
            sa.select(WeeklyEventModel)
            .order_by(WeeklyEventModel.start, WeeklyEventModel.id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(q)
        return list(result.scalars().all())
