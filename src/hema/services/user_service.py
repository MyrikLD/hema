import json
from io import BytesIO

import qrcode
import qrcode.image.svg
import sqlalchemy as sa
from qrcode import QRCode
from qrcode.constants import ERROR_CORRECT_H
from sqlalchemy.ext.asyncio import AsyncSession

from hema.auth import password_hashing
from hema.models import UserModel
from hema.models.trainers import TrainerModel
from hema.schemas.users import UserCreateSchema, UserProfileUpdateShema


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user_profile(
        self,
        new_user_data: UserCreateSchema,
    ) -> dict | None:
        if new_user_data.phone:
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
        q = (
            sa.select(*UserModel.__table__.c, TrainerModel.id.isnot(None).label("is_trainer"))
            .outerjoin(TrainerModel, TrainerModel.id == UserModel.id)
            .where(UserModel.id == user_id)
        )
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
        if "password" in data:
            data["password"] = password_hashing(data["password"])
        q = (
            sa.update(UserModel)
            .where(UserModel.id == user_id)
            .values(**data)
            .returning(*UserModel.__table__.c)
        )
        return (await self.db.execute(q)).mappings().first()

    @staticmethod
    def qr_gen(user_id: int) -> bytes:
        qr = QRCode(error_correction=ERROR_CORRECT_H)
        qr.add_data(json.dumps({"user_id": user_id}))
        image = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)

        with BytesIO() as buffer:
            image.save(buffer)
            return buffer.getvalue()
