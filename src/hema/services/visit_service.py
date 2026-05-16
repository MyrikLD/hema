from sqlalchemy.exc import IntegrityError
from hema.exceptions import AlreadyMarkedError, NotATrainerError
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from hema.models import EventModel, VisitModel, UserModel
from hema.models.trainers import TrainerModel
from hema.schemas.visits import VisitMarkPostSchema


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
        is_trainer = await self.db.scalar(
            sa.select(TrainerModel.id).where(TrainerModel.id == trainer_id)
        )
        if not is_trainer:
            raise NotATrainerError()
        q = (
            sa.select(
                EventModel.name.label("event_name"),
                UserModel.username,
            )
            .select_from(EventModel)
            .outerjoin(UserModel, UserModel.id == data.user_id)
            .where(EventModel.id == data.event_id)
        )
        row = (await self.db.execute(q)).mappings().first()
        if not row:
            raise NotATrainerError()
        q_insert = (
            sa.insert(VisitModel)
            .values(user_id=data.user_id, event_id=data.event_id, uid=str(data.user_id))
            .returning(VisitModel.timestamp)
        )
        try:
            timestamp = await self.db.scalar(q_insert)
        except IntegrityError:
            raise AlreadyMarkedError(username=row["username"])
        return {
            "status": "marked",
            "timestamp": timestamp,
            "event_name": row["event_name"],
            "username": row["username"],
        }
