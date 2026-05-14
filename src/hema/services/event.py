from datetime import date, datetime, timedelta

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from hema.models import EventModel
from hema.models.users import UserModel
from hema.schemas.events import EventCreateSchema, EventResponse


class EventService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _with_trainer(self):
        return sa.select(*EventModel.__table__.c, UserModel.name.label("trainer_name")).outerjoin(
            UserModel, EventModel.trainer_id == UserModel.id
        )

    async def by_id(self, event_id: int) -> EventResponse:
        q = self._with_trainer().where(EventModel.id == event_id)
        r = (await self.session.execute(q)).mappings().one_or_none()
        return EventResponse.model_validate(r)

    async def list_events(
        self, start: date, end: date, trainer_id: int | None = None
    ) -> list[EventResponse]:
        q = self._with_trainer().where(EventModel.date >= start).where(EventModel.date <= end)
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
        return await self.by_id(event_id)  # type: ignore[arg-type]

    async def set_trainer(self, event_id: int, user_id: int):
        q = (
            sa.update(EventModel)
            .where(EventModel.id == event_id)
            .values({EventModel.trainer_id.name: user_id})
        )
        await self.session.execute(q)
        return await self.by_id(event_id)

    async def check_event_time(self, trainer_id: int) -> list[EventResponse]:
        now = datetime.now()
        now_time = now.time()
        future_time = (now + timedelta(minutes=30)).time()
        q = sa.select(*EventModel.__table__.c).where(
            EventModel.date == date.today(),
            EventModel.time_start <= future_time,
            EventModel.time_end > now_time,
            EventModel.trainer_id == trainer_id,
        )
        result = (await self.session.execute(q)).mappings().all()
        return list(map(EventResponse.model_validate, result))
