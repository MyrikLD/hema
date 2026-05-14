from sqlalchemy.exc import IntegrityError
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from hema.models import EventModel, VisitModel, UserModel
from hema.schemas.visits import VisitMarkPostSchema, VisitMarkResponseSchema


class VisitService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_visits(self, user_id: int, limit: int = 50, offset: int = 0) -> list[dict]:
        q = (
            sa.select(
                VisitModel.timestamp,
                VisitModel.uid,
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

    async def mark_visit(self, data: VisitMarkPostSchema, trainer_id: int) -> dict:
        event_trainer_id = await self.db.scalar(
            sa.select(EventModel.trainer_id).where(EventModel.id == data.event_id)
        )
        if event_trainer_id != trainer_id:
            return {"status": "forbidden"}
        q = (
            sa.insert(VisitModel)
            .values(user_id=data.user_id, event_id=data.event_id, uid=str(data.user_id))
            .returning(*VisitModel.__table__.c)
        )
        try:
            async with self.db.begin_nested():
                row = await self.db.execute(q)
                result = row.mappings().first()
            await self.db.flush()
            event = await self.db.scalar(
                sa.select(EventModel.name).where(EventModel.id == data.event_id)
            )
            username = await self.db.scalar(
                sa.select(UserModel.username).where(UserModel.id == data.user_id)
            )
            return {
                "status": "marked",
                "timestamp": result["timestamp"],
                "event_name": event,
                "username": username,
            }
        except IntegrityError as e:
            print(e)
            return {"status": "already_marked"}
