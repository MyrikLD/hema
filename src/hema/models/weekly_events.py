import sqlalchemy as sa

from .base import Base


class WeeklyEventModel(Base):
    __tablename__ = "weekly_events"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    start = sa.Column(sa.Date, nullable=False)
    end = sa.Column(sa.Date, nullable=False)

    name = sa.Column(sa.String, nullable=False)
    color = sa.Column(sa.String(6), nullable=False, default="4CAF50")
    weekday = sa.Column(sa.SmallInteger, nullable=False)  # 0=Monday … 6=Sunday
    time_start = sa.Column(sa.Time, nullable=False)
    time_end = sa.Column(sa.Time, nullable=False)
    trainer_id = sa.Column(sa.Integer, sa.ForeignKey("trainers.id", ondelete="SET NULL"))

    price = sa.Column(sa.Integer, server_default="0", nullable=False)
