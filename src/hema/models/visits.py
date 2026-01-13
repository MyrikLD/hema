import sqlalchemy as sa

from .base import Base


class VisitModel(Base):
    __tablename__ = "visits"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    timestamp = sa.Column(sa.DateTime, nullable=False)
    uid = sa.Column(sa.String(), nullable=False)

    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    event_id = sa.Column(sa.Integer, sa.ForeignKey("events.id"), nullable=True)
