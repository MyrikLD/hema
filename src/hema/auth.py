"""Basic authentication dependencies for API routes."""

from datetime import datetime, timedelta, UTC

import jwt
import sqlalchemy as sa
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jwt import algorithms, PyJWTError
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_401_UNAUTHORIZED

from hema.config import settings
from hema.db import db
from hema.models import UserModel

password_hash = PasswordHash.recommended()


class OAuthPasswordBearer(OAuth2PasswordBearer):
    def __init__(self, token_url: str):
        super().__init__(tokenUrl=token_url)

    async def __call__(self, request: Request, session: AsyncSession = Depends(db.get_db)) -> int:
        token = await super().__call__(request)
        payload = self.verify_jwt_token(token=token)
        user_id = payload["user_id"]
        check_user = await self.check_current_user(user_id, session)
        return check_user

    @staticmethod
    def verify_jwt_token(token: str) -> dict:
        if not algorithms.has_crypto:
            raise Exception("No crypto support for JWT, please install the cryptography dependency")

        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        except PyJWTError:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token error")

        return decoded_token

    @staticmethod
    async def check_current_user(user_id: int, session: AsyncSession) -> int:
        q = sa.select(UserModel.id).where(UserModel.id == user_id)
        user_id = await session.scalar(q)
        if not user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user_id


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def password_hashing(user_password: str):
    return password_hash.hash(user_password)


def create_jwt_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    token = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return token


oauth2_scheme = OAuthPasswordBearer(token_url="/api/users/login")
