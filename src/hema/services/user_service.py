import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from hema.models import UserModel, VisitModel
from hema.schemas.users import UserCreateSchema, UserProfileUpdateShema


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user_profile(
        self,
        new_user_data: UserCreateSchema,
    ) -> dict | None:
        q = sa.select(UserModel.id).where(UserModel.phone == new_user_data.phone)
        if await self.db.scalar(q):
            return None
        q = (
            sa.insert(UserModel)
            .values(**new_user_data.model_dump())
            .returning(*UserModel.__table__.c)
        )
        return (await self.db.execute(q)).mappings().first()

    async def get(self, user_id: int) -> dict | None:
        q = sa.select(*UserModel.__table__.c).where(UserModel.id == user_id)
        return (await self.db.execute(q)).mappings().first()

    async def update_user_profile(
        self, user_id: int, update_data: UserProfileUpdateShema
    ) -> dict | None:
        data = update_data.model_dump(exclude_unset=True)
        if not data:
            return await self.get(user_id)
        q = (
            sa.update(UserModel)
            .where(UserModel.id == user_id)
            .values(**data)
            .returning(*UserModel.__table__.c)
        )
        return (await self.db.execute(q)).mappings().first()

    async def attach_uid(self, user_id: int, uid: str) -> dict | None:
        q = (
            sa.update(UserModel)
            .where(UserModel.id == user_id)
            .values({UserModel.rfid_uid.name: uid})
            .returning(*UserModel.__table__.c)
        )
        r = (await self.db.execute(q)).mappings().first()

        q = (
            sa.update(VisitModel)
            .where(VisitModel.uid == uid)
            .where(VisitModel.user_id.is_(None))
            .values({VisitModel.user_id: user_id})
        )
        await self.db.execute(q)

        return r
