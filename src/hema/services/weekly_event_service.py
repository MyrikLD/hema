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
        weekday: int,
        time_start,
        time_end,
        start: date,
        end: date,
        weekly_event_id: int,
        trainer_id: int,
    ) -> int:
        existing = set(
            (
                await self.db.scalars(
                    sa.select(EventModel.date).where(EventModel.weekly_id == weekly_event_id)
                )
            ).all()
        )

        items = []
        current_date = start
        while current_date <= end:
            if current_date.weekday() == weekday and current_date not in existing:
                items.append(
                    {
                        EventModel.name: name,
                        EventModel.color: color,
                        EventModel.date: current_date,
                        EventModel.time_start: time_start,
                        EventModel.time_end: time_end,
                        EventModel.weekly_id: weekly_event_id,
                        EventModel.trainer_id: trainer_id,
                    }
                )
            current_date += timedelta(days=1)

        if items:
            await self.db.execute(sa.insert(EventModel).values(items))

        return len(items)

    async def sync_future_events(self) -> int:
        """Generate missing future events for all active weekly events. Safe to call on startup."""
        q = sa.select(WeeklyEventModel).where(WeeklyEventModel.end >= datetime.now().date())
        weekly_events = (await self.db.execute(q)).scalars().all()
        total = 0
        for we in weekly_events:
            total += await self.generate_events(
                name=we.name,
                color=we.color,
                weekday=we.weekday,
                time_start=we.time_start,
                time_end=we.time_end,
                start=we.start,
                end=we.end,
                weekly_event_id=we.id,
                trainer_id=we.trainer_id,
            )
        return total

    async def create_weekly_event(self, data: WeeklyEventCreate, user_id: int) -> dict:
        weekly_event_id = await self.db.scalar(
            sa.insert(WeeklyEventModel)
            .values(
                {
                    WeeklyEventModel.start: data.start,
                    WeeklyEventModel.end: data.end,
                    WeeklyEventModel.name: data.name,
                    WeeklyEventModel.color: data.color,
                    WeeklyEventModel.weekday: data.weekday,
                    WeeklyEventModel.time_start: data.time_start,
                    WeeklyEventModel.time_end: data.time_end,
                    WeeklyEventModel.trainer_id: user_id,
                }
            )
            .returning(WeeklyEventModel.id)
        )

        await self.generate_events(
            name=data.name,
            color=data.color,
            weekday=data.weekday,
            time_start=data.time_start,
            time_end=data.time_end,
            start=data.start,
            end=data.end,
            trainer_id=user_id,
            weekly_event_id=weekly_event_id,  # type: ignore[arg-type]
        )

        return await self.get_weekly_event(weekly_event_id)  # type: ignore[arg-type]

    async def update_weekly_event(
        self, weekly_event_id: int, data: WeeklyEventUpdate
    ) -> dict | None:
        q = sa.select(*WeeklyEventModel.__table__.c).where(WeeklyEventModel.id == weekly_event_id)
        weekly_event = (await self.db.execute(q)).mappings().fetchone()

        if not weekly_event:
            return None

        _data = data.model_dump(exclude_unset=True)

        schedule_changed = any(
            _data.get(f) is not None and _data[f] != weekly_event[f]
            for f in ("start", "end", "weekday")
        )

        await self.db.execute(
            sa.update(WeeklyEventModel).where(WeeklyEventModel.id == weekly_event_id).values(_data)
        )

        today = datetime.now().date()

        if schedule_changed:
            await self.db.execute(
                sa.delete(EventModel).where(
                    EventModel.weekly_id == weekly_event_id,
                    EventModel.date > today,
                )
            )
            we = {**weekly_event, **_data}
            await self.generate_events(
                name=we["name"],
                color=we["color"],
                weekday=we["weekday"],
                time_start=we["time_start"],
                time_end=we["time_end"],
                start=we["start"],
                end=we["end"],
                trainer_id=we["trainer_id"],
                weekly_event_id=weekly_event_id,
            )
        else:
            we = {**weekly_event, **_data}
            await self.db.execute(
                sa.update(EventModel)
                .where(
                    EventModel.weekly_id == weekly_event_id,
                    EventModel.date > today,
                )
                .values(
                    name=we["name"],
                    color=we["color"],
                    trainer_id=we["trainer_id"],
                    time_start=we["time_start"],
                    time_end=we["time_end"],
                )
            )

        return await self.get_weekly_event(weekly_event_id)

    async def delete_weekly_event(self, weekly_event_id: int) -> bool:
        today = datetime.now().date()

        await self.db.execute(
            sa.update(EventModel)
            .where(EventModel.weekly_id == weekly_event_id, EventModel.date > today)
            .values({EventModel.weekly_id: None})
        )

        result = await self.db.execute(
            sa.delete(WeeklyEventModel).where(WeeklyEventModel.id == weekly_event_id)
        )

        return result.rowcount > 0  # type: ignore[attr-defined]

    async def get_weekly_event(self, weekly_event_id: int) -> dict | None:
        q = sa.select(*WeeklyEventModel.__table__.c).where(WeeklyEventModel.id == weekly_event_id)
        return (await self.db.execute(q)).mappings().fetchone()

    async def list_weekly_events(
        self, start: date | None = None, end: date | None = None
    ) -> list[WeeklyEventModel]:
        q = sa.select(WeeklyEventModel).order_by(
            WeeklyEventModel.weekday, WeeklyEventModel.time_start
        )
        if start is not None:
            q = q.where(WeeklyEventModel.end >= start)
        if end is not None:
            q = q.where(WeeklyEventModel.start <= end)
        return list((await self.db.execute(q)).scalars().all())
