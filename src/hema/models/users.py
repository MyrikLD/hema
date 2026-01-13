import sqlalchemy as sa
from hema.schemas.users import UserGender
from .base import Base


class UserModel(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(), nullable=False)
    password = sa.Column(sa.String(), nullable=False)
    gender = sa.Column(sa.String(), nullable=True, default=UserGender.OTHER)
    phone = sa.Column(sa.String(), nullable=True)
    rfid_uid = sa.Column(sa.String(), nullable=True)
    is_trainer = sa.Column(sa.Boolean(), nullable=False, server_default=sa.text("false"))
