import sqlalchemy as sa
from .base import Base


class VisitModel(Base):
    __tablename__ = "visits"

    timestamp = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())
    uid = sa.Column(sa.String(), nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_id = sa.Column(sa.Integer, sa.ForeignKey("events.id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (
        sa.PrimaryKeyConstraint("timestamp", "uid"),
        sa.UniqueConstraint("user_id", "event_id"),
    )
