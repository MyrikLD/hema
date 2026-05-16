import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from hema.models import EventModel, UserPaymentHistory, VisitModel


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_deposit(
        self,
        trainer_id: int,
        user_id: int,
        payment: int,
        comment: str | None = None,
    ) -> dict:
        q = (
            sa.insert(UserPaymentHistory)
            .values(
                {
                    UserPaymentHistory.user_id: user_id,
                    UserPaymentHistory.payment: payment,
                    UserPaymentHistory.comment: comment,
                    UserPaymentHistory.trainer_id: trainer_id,
                }
            )
            .returning(*UserPaymentHistory.__table__.c)
        )
        return (await self.db.execute(q)).mappings().first()

    async def get_user_payment_history(self, user_id: int) -> list[dict]:
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
        q = sa.select(sa.func.sum(UserPaymentHistory.payment)).where(
            UserPaymentHistory.user_id == user_id
        )
        payments = await self.db.scalar(q)

        q = (
            sa.select(sa.func.sum(EventModel.price))
            .join(VisitModel, EventModel.id == VisitModel.event_id)
            .where(VisitModel.user_id == user_id)
        )
        debt = await self.db.scalar(q)

        return (payments or 0) - (debt or 0)
