import sqlalchemy as sa

from .base import Base


class IntentionModel(Base):
    __tablename__ = "intentions"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    event_id = sa.Column(sa.Integer, sa.ForeignKey("events.id"))
