import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from hema.models import UserModel
from hema.schemas.users import UserCreateSchema, UserProfileUpdateShema


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user_profile(
        self,
        new_user_data: UserCreateSchema,
    ) -> UserModel | None:
        q = sa.select(UserModel).where(UserModel.phone == new_user_data.phone)
        if await self.db.scalar(q):
            return None
        q = sa.insert(UserModel).values(**new_user_data.model_dump()).returning(UserModel)
        return await self.db.scalar(q)

    async def get_user_profile(self, user_id: int) -> UserModel | None:
        q = sa.select(UserModel).where(UserModel.id == user_id)
        return await self.db.scalar(q)

    async def update_user_profile(
        self, user_id: int, update_data: UserProfileUpdateShema
    ) -> UserModel | None:
        data = update_data.model_dump(exclude_unset=True)
        if not data:
            return await self.get_user_profile(user_id)
        q = sa.update(UserModel).where(UserModel.id == user_id).values(**data).returning(UserModel)
        return await self.db.scalar(q)
