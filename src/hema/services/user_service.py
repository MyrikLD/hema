import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from hema.auth import password_hashing
from hema.models import UserModel, VisitModel, UserPaymentHistory, EventModel, TrainerModel
from hema.schemas.payments import PaymentUpdateShema
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
            raise ValueError("Phone number already exists")
        with_password = new_user_data.model_copy(
            update={"password": password_hashing(new_user_data.password)}
        )
        values = with_password.model_dump(mode="json", exclude_unset=True)
        q = sa.insert(UserModel).values(values).returning(*UserModel.__table__.c)
        return (await self.db.execute(q)).mappings().first()

    async def get_by_id(self, user_id: int) -> dict | None:
        q = sa.select(*UserModel.__table__.c).where(UserModel.id == user_id)
        return (await self.db.execute(q)).mappings().first()

    async def get_by_username(self, username: str) -> dict | None:
        q = sa.select(*UserModel.__table__.c).where(UserModel.username == username)
        result = (await self.db.execute(q)).mappings().first()
        return result

    async def update_user_profile(
        self, user_id: int, update_data: UserProfileUpdateShema
    ) -> dict | None:
        data = update_data.model_dump(exclude_unset=True)
        if not data:
            return await self.get_by_id(user_id)
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
