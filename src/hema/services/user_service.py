import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from hema.auth import password_hashing
from hema.models import UserModel, VisitModel, UserPaymentHistory, EventModel, TrainerModel
from hema.schemas.payments import DepositUpdateShema, DeleteUserPayment
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

    async def update_user_deposit(
        self, payment_data: DepositUpdateShema, trainer_id: int
    ) -> dict | None:
        updated_data = payment_data.model_dump(mode="json", exclude_unset=True)
        updated_data["trainer_id"] = trainer_id
        if not updated_data:
            return await self.get_user_balance(updated_data["user_id"])
        q = (
            sa.insert(UserPaymentHistory)
            .values(updated_data)
            .returning(*UserPaymentHistory.__table__.c)
        )
        return (await self.db.execute(q)).mappings().first()

    async def get_user_payment_history(self, user_id: int) -> list[dict] | None:
        q = sa.select(*UserPaymentHistory.__table__.c).where(UserPaymentHistory.user_id == user_id)
        return (await self.db.execute(q)).mappings().all()

    async def delete_user_payment(self, payment_id: DeleteUserPayment) -> dict | None:
        id = payment_id.model_dump(mode="json", exclude_unset=True)
        q = (
            sa.delete(UserPaymentHistory)
            .where(UserPaymentHistory.id == id["id"])
            .returning(*UserPaymentHistory.__table__.c)
        )
        return (await self.db.execute(q)).mappings().first()

    async def get_user_balance(self, user_id: int) -> dict | None:
        payments_sum = (
            sa.select(sa.func.sum(UserPaymentHistory.payment).label("total_payment"))
            .where(UserPaymentHistory.user_id == user_id)
            .subquery()
        )
        debt_sum = (
            sa.select(sa.func.sum(EventModel.price).label("total_debt"))
            .join(VisitModel, EventModel.id == VisitModel.event_id)
            .where(VisitModel.user_id == user_id)
            .subquery()
        )
        q = sa.select(payments_sum, debt_sum)
        result = (await self.db.execute(q)).mappings().first()
        debt = result.get("total_debt") or 0
        payments = result.get("total_payment") or 0
        return {"balance": payments - debt}
