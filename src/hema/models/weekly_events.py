import sqlalchemy as sa

from .base import Base


class WeeklyEventModel(Base):
    __tablename__ = "weekly_events"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    start = sa.Column(sa.Date)
    end = sa.Column(sa.Date)

    # Event default values
    name = sa.Column(sa.String)
    color = sa.Column(sa.String(6), nullable=False, default="4CAF50")
    event_start = sa.Column(sa.DateTime)
    event_end = sa.Column(sa.DateTime)
    trainer_id = sa.Column(sa.Integer, sa.ForeignKey("trainers.id", ondelete="SET NULL"))
