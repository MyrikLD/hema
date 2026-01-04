import sqlalchemy as sa

from .base import Base


class UserModel(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(), nullable=False)
    email = sa.Column(sa.String(), nullable=False)
    password = sa.Column(sa.String(), nullable=False)
    rfid_uid = sa.Column(sa.String(), nullable=False)
