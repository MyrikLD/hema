import sqlalchemy as sa

from hema.schemas.users import UserGender
from .base import Base


class UserModel(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(), nullable=False, unique=True)
    password = sa.Column(sa.String(), nullable=False)
    phone = sa.Column(sa.String(), nullable=True, unique=True)

    gender = sa.Column(sa.String(), nullable=True, default=UserGender.OTHER)

    rfid_uid = sa.Column(sa.String(), nullable=True, unique=True)
