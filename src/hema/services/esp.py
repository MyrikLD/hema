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
        q = sa.select(EventModel.id, EventModel.date, EventModel.time_start, EventModel.time_end).where(
            EventModel.date >= start.date(),
            EventModel.date <= end.date(),
        )
        self.event_ids = {}
        for row in (await session.execute(q)).mappings().all():
            ev_start = datetime.combine(row["date"], row["time_start"])
            ev_end = datetime.combine(row["date"], row["time_end"])
            self.event_ids[row["id"]] = (ev_start, ev_end)

    def get(self, ts: datetime) -> int | None:
        for i, (start, end) in self.event_ids.items():
            if start <= ts <= end:
                return i
