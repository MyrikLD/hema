import sqlalchemy as sa

from .base import Base


class VisitModel(Base):
    __tablename__ = "visits"

    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    event_id = sa.Column(
        sa.Integer, sa.ForeignKey("events.id", ondelete="RESTRICT"), nullable=False
    )
    trainer_id = sa.Column(
        sa.Integer, sa.ForeignKey("trainers.id", ondelete="RESTRICT"), nullable=False
    )
    timestamp = sa.Column(sa.DateTime, nullable=False, server_default=sa.text("now()"))

    __table_args__ = (sa.PrimaryKeyConstraint("user_id", "event_id"),)
