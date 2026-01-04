import sqlalchemy as sa

from .base import Base


class EventModel(Base):
    __tablename__ = "events"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    name = sa.Column(sa.String)

    start = sa.Column(sa.DateTime)
    end = sa.Column(sa.DateTime)

    trainer_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
