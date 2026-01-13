from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from hema.models import EventModel
from hema.schemas.events import EventCreateSchema, EventResponse


class EventService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def by_id(self, event_id: int) -> EventResponse:
        q = sa.select(
            *EventModel.__table__.c,
        ).where(EventModel.id == event_id)
        r = (await self.session.execute(q)).mappings().one_or_none()
        return EventResponse.model_validate(r)

    async def list_events(
        self, start: datetime, end: datetime, trainer_id: int | None = None
    ) -> list[EventResponse]:
        q = (
            sa.select(
                *EventModel.__table__.c,
            )
            .where(EventModel.start >= start)
            .where(EventModel.end <= end)
        )
        if trainer_id:
            q = q.where(EventModel.trainer_id == trainer_id)

        r = (await self.session.execute(q)).mappings().all()
        return list(map(EventResponse.model_validate, r))

    async def create(self, event_data: EventCreateSchema, user_id: int) -> EventResponse:
        q = (
            sa.insert(EventModel)
            .values(
                {
                    EventModel.trainer_id.name: user_id,
                    **event_data.model_dump(),
                }
            )
            .returning(EventModel.id)
        )
        event_id = await self.session.scalar(q)
        return await self.by_id(event_id)

    async def set_trainer(self, event_id: int, user_id: int):
        q = (
            sa.update(EventModel)
            .where(EventModel.id == event_id)
            .values({EventModel.trainer_id.name: user_id})
        )
        await self.session.execute(q)
        return await self.by_id(event_id)
