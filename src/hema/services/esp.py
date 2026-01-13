from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from hema.models import EventModel
from hema.models.users import UserModel


class UserMapper:
    def __init__(self):
        self.user_ids = dict()

    async def load(self, session: AsyncSession, uids: set[str]):
        q = sa.select(UserModel.rfid_uid, UserModel.id).where(UserModel.rfid_uid.in_(uids))
        response = (await session.execute(q)).all()
        self.user_ids = dict(response)

    def get(self, uuid) -> int | None:
        return self.user_ids.get(uuid)


class EventMapper:
    def __init__(self):
        self.event_ids = dict()

    async def load(self, session: AsyncSession, start, end):
        q = (
            sa.select(EventModel.id, EventModel.start, EventModel.end)
            .where(EventModel.start <= start)
            .where(EventModel.end >= end)
        )
        self.event_ids = {
            i["id"]: (i["start"], i["end"]) for i in (await session.execute(q)).mappings().all()
        }

    def get(self, ts: datetime) -> int | None:
        for i, (start, end) in self.event_ids.items():
            if start <= ts <= end:
                return i
