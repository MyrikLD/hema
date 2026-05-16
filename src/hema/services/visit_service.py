import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hema.exceptions import AlreadyExists
from hema.models import EventModel, VisitModel


class VisitService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_visits(self, user_id: int, limit: int = 50, offset: int = 0) -> list[dict]:
        q = (
            sa.select(
                VisitModel.timestamp,
                VisitModel.user_id,
                VisitModel.event_id,
                EventModel.name.label("event_name"),
                EventModel.color.label("event_color"),
            )
            .outerjoin(EventModel, VisitModel.event_id == EventModel.id)
            .where(VisitModel.user_id == user_id)
            .order_by(VisitModel.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )
        return list((await self.db.execute(q)).mappings().all())

    async def mark_visit(self, user_id: int, event_id: int, trainer_id: int) -> None:
        q = sa.insert(VisitModel).values(
            {
                VisitModel.user_id: user_id,
                VisitModel.event_id: event_id,
                VisitModel.trainer_id: trainer_id,
            }
        )

        try:
            await self.db.execute(q)
        except IntegrityError:
            raise AlreadyExists()
