import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from hema.models.users import UserModel
from hema.schemas.users import UserCreateSchema, UserCreateResponseSchema
from hema.models import UserModel
from sqlalchemy import or_

class UserService:
    def __init__(self, db:AsyncSession):
        self.db = db


    async def create_user_profile(self,
                        new_user_data : UserCreateSchema,
                        ) -> UserModel | None:
        q = sa.select(UserModel).where(UserModel.phone == new_user_data.phone)
        if await self.db.scalar(q):
            return None
        user = UserModel(**new_user_data.model_dump())
        self.db.add(user)
        return user

