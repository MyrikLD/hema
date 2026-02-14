from .base import Base
import sqlalchemy as sa


class UserPaymentHistory(Base):
    __tablename__ = "payment_history"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    trainer_id = sa.Column(sa.Integer, sa.ForeignKey("trainers.id"))
    payment = sa.Column(sa.Integer)
    timestamp = sa.Column(sa.DateTime, server_default=sa.func.now())
    comment = sa.Column(sa.String, nullable=True)
