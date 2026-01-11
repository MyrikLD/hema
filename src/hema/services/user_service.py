import datetime
from typing import Dict

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from watchfiles import awatch
from hema.schemas.events import EventBase
from hema.models import UserModel, EventModel
from hema.models.intentions import IntentionModel
from hema.schemas.users import UserCreateSchema, UserProfileUpdateShema


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user_profile(
        self,
        new_user_data: UserCreateSchema,
    ) -> dict | None:
        q = sa.select(UserModel).where(UserModel.phone == new_user_data.phone)
        if await self.db.scalar(q):
            return None
        q = (
            sa.insert(UserModel)
            .values(**new_user_data.model_dump())
            .returning(UserModel)
        )
        return await self.db.scalar(q)

    async def get_user_profile(self, user_id: int) -> dict | None:
        q = sa.select(UserModel).where(UserModel.id == user_id)
        return await self.db.scalar(q)

    async def update_user_profile(
        self, user_id: int, update_data: UserProfileUpdateShema
    ) -> dict | None:
        data = update_data.model_dump(exclude_unset=True)
        if not data:
            return await self.get_user_profile(user_id)
        q = (
            sa.update(UserModel)
            .where(UserModel.id == user_id)
            .values(**data)
            .returning(UserModel)
        )
        return await self.db.scalar(q)

    async def create_event(self, event_data: EventBase) -> dict | None:
        data = event_data.model_dump()
        data["start"] = data["start"].replace(tzinfo=None)
        data["end"] = data["end"].replace(tzinfo=None)
        if not data.get("weekly_id"):
            data.pop("weekly_id", None)
        q = sa.insert(EventModel).values(**data).returning(EventModel)
        return await self.db.scalar(q)

    async def get_trainer_events(self, user_id: int) -> list[dict] | None:
        q = sa.select(EventModel).where(EventModel.trainer_id == user_id)
        result = await self.db.scalars(q)
        if not result:
            return None
        trainers_events = list(result.all())
        return trainers_events
