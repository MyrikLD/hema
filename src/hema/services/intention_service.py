import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from hema.models.intentions import IntentionModel


class IntentionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int, event_id: int) -> dict | None:
        existing = await self.db.scalar(
            sa.select(IntentionModel.id)
            .where(IntentionModel.user_id == user_id)
            .where(IntentionModel.event_id == event_id)
        )
        if existing:
            return None

        q = (
            sa.insert(IntentionModel)
            .values(user_id=user_id, event_id=event_id)
            .returning(*IntentionModel.__table__.c)
        )
        return (await self.db.execute(q)).mappings().first()

    async def delete(self, user_id: int, event_id: int) -> bool:
        q = (
            sa.delete(IntentionModel)
            .where(IntentionModel.user_id == user_id)
            .where(IntentionModel.event_id == event_id)
        )
        result = await self.db.execute(q)
        return result.rowcount > 0

    async def get_for_event(self, event_id: int) -> list[dict]:
        from hema.models import UserModel

        q = (
            sa.select(
                IntentionModel.id,
                IntentionModel.user_id,
                IntentionModel.event_id,
                UserModel.name.label("user_name"),
            )
            .join(UserModel, IntentionModel.user_id == UserModel.id)
            .where(IntentionModel.event_id == event_id)
        )
        return list((await self.db.execute(q)).mappings().all())

    async def has_intention(self, user_id: int, event_id: int) -> bool:
        q = (
            sa.select(IntentionModel.id)
            .where(IntentionModel.user_id == user_id)
            .where(IntentionModel.event_id == event_id)
        )
        return (await self.db.scalar(q)) is not None
