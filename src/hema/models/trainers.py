import sqlalchemy as sa

from .base import Base


class TrainerModel(Base):
    __tablename__ = "trainers"

    id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), primary_key=True)
