import sqlalchemy as sa

from .base import Base


class EventModel(Base):
    __tablename__ = "events"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    name = sa.Column(sa.String, nullable=False)
    color = sa.Column(sa.String(6), nullable=False, default="4CAF50")

    date = sa.Column(sa.Date, nullable=False)
    time_start = sa.Column(sa.Time, nullable=False)
    time_end = sa.Column(sa.Time, nullable=False)

    weekly_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("weekly_events.id", ondelete="CASCADE"),
        nullable=True,
    )
    trainer_id = sa.Column(sa.Integer, sa.ForeignKey("trainers.id", ondelete="SET NULL"))

    price = sa.Column(sa.Integer, server_default="0")
