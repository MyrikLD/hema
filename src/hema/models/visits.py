import sqlalchemy as sa

from .base import Base


class VisitModel(Base):
    __tablename__ = "visits"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    timestamp = sa.Column(sa.DateTime)
