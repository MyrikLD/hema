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

    async def generate_events(self, weekly_event_id: int) -> int:
        q = sa.select(WeeklyEventModel.start, WeeklyEventModel.end, WeeklyEventModel.weekday).where(
            WeeklyEventModel.id == weekly_event_id
        )
        start, end, weekday = (await self.db.execute(q)).fetchone()

        existing = set(
            await self.db.scalars(
                sa.select(EventModel.date).where(EventModel.weekly_id == weekly_event_id)
            )
        )

        dates = []
        current = max(start, date.today())
        while current <= end:
            if current.weekday() == weekday and current not in existing:
                dates.append((current,))
            current += timedelta(days=1)

        if not dates:
            return 0

        dates_tbl = sa.values(sa.column("d", sa.Date), name="dates").data(dates)

        sel = (
            sa.select(
                WeeklyEventModel.name,
                WeeklyEventModel.color,
                dates_tbl.c.d.label("date"),
                WeeklyEventModel.time_start,
                WeeklyEventModel.time_end,
                sa.literal(weekly_event_id).label("weekly_id"),
                WeeklyEventModel.trainer_id,
                WeeklyEventModel.price,
            )
            .select_from(dates_tbl)
            .join(WeeklyEventModel, WeeklyEventModel.id == weekly_event_id)
        )

        result = await self.db.execute(
            sa.insert(EventModel).from_select(
                [
                    "name",
                    "color",
                    "date",
                    "time_start",
                    "time_end",
                    "weekly_id",
                    "trainer_id",
                    "price",
                ],
                sel,
            )
        )
        return result.rowcount

    async def sync_future_events(self) -> int:
        """Generate missing future events for all active weekly events. Safe to call on startup."""
        ids = await self.db.scalars(
            sa.select(WeeklyEventModel.id).where(WeeklyEventModel.end >= datetime.now().date())
        )
        total = 0
        for weekly_event_id in ids.all():
            total += await self.generate_events(weekly_event_id)
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
                    WeeklyEventModel.price: data.price,
                    WeeklyEventModel.trainer_id: user_id,
                }
            )
            .returning(WeeklyEventModel.id)
        )

        await self.generate_events(weekly_event_id)  # type: ignore[arg-type]

        return await self.get_weekly_event(weekly_event_id)  # type: ignore[arg-type]

    async def update_weekly_event(
        self, weekly_event_id: int, data: WeeklyEventUpdate
    ) -> dict | None:
        curr_weekday = await self.db.scalar(
            sa.select(WeeklyEventModel.weekday).where(WeeklyEventModel.id == weekly_event_id)
        )

        _data = data.model_dump(exclude_unset=True)

        await self.db.execute(
            sa.update(WeeklyEventModel).where(WeeklyEventModel.id == weekly_event_id).values(_data)
        )

        today = date.today()

        if _data.get("weekday") is not None and curr_weekday != _data["weekday"]:
            await self.db.execute(
                sa.delete(EventModel).where(
                    EventModel.weekly_id == weekly_event_id, EventModel.date > today
                )
            )
            await self.generate_events(weekly_event_id)
        else:
            we_tbl = WeeklyEventModel.__table__.c
            await self.db.execute(
                sa.update(EventModel)
                .values(
                    name=we_tbl.name,
                    color=we_tbl.color,
                    trainer_id=we_tbl.trainer_id,
                    time_start=we_tbl.time_start,
                    time_end=we_tbl.time_end,
                )
                .where(EventModel.weekly_id == weekly_event_id, EventModel.date > today)
                .where(we_tbl.id == weekly_event_id)
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
