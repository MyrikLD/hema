import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from hema.models import UserModel, VisitModel, UserPaymentHistory, EventModel, TrainerModel
from hema.schemas.payments import PaymentUpdateSchema


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_user_deposit(self, payment_data: PaymentUpdateSchema, trainer_id: int) -> dict:
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

    async def delete_user_payment(self, payment_id: int) -> bool:
        q = (
            sa.delete(UserPaymentHistory)
            .where(UserPaymentHistory.id == payment_id)
            .returning(*UserPaymentHistory.id)
        )
        return (await self.db.scalar(q)) is not None

    async def get_user_balance(self, user_id: int) -> int:
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
        return payments - debt
