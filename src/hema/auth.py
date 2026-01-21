"""Basic authentication dependencies for API routes."""

from datetime import datetime, timedelta
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
import sqlalchemy as sa
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_401_UNAUTHORIZED
from dotenv import load_dotenv

from hema.config import settings
from hema.db import db
from hema.models import UserModel
from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


class OAuthPasswordBearer(OAuth2PasswordBearer):
    def __init__(
        self,
        tokenUrl: str,
    ):
        super().__init__(tokenUrl=tokenUrl)

    async def __call__(self, request: Request, session: AsyncSession = Depends(db.get_db)):
        token = await super().__call__(request)
        payload = self.verify_jwt_token(token=token)
        user_id = payload["user_id"]
        check_user = await self.check_current_user(user_id, session)
        return check_user

    @staticmethod
    def verify_jwt_token(token: str) -> dict | None:
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
            return decoded_token
        except InvalidTokenError:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token error")

    @staticmethod
    async def check_current_user(user_id: int, session: AsyncSession) -> dict | None:
        q = sa.select(UserModel.id).where(UserModel.id == user_id)
        user_id = await session.scalar(q)
        if not user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user_id


def verify_password(plain_password, hashed_password) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def password_hashing(user_password: str):
    return password_hash.hash(user_password)


def create_jwt_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    token = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return token


oauth2_scheme = OAuthPasswordBearer(tokenUrl="/api/users/login")


class HTTPBasicAuth(HTTPBasic):
    async def __call__(self, request: Request, session: AsyncSession = Depends(db.get_db)) -> int:
        credentials: HTTPBasicCredentials = await super().__call__(request)

        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing credentials",
                headers=self.make_authenticate_headers(),
            )

        user_id = await self.verify(session, credentials)

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing user",
                headers=self.make_authenticate_headers(),
            )

        return user_id

    @staticmethod
    async def verify(session: AsyncSession, credentials: HTTPBasicCredentials) -> int | None:
        q = sa.select(UserModel.id).where(
            UserModel.name == credentials.username,
            UserModel.password == credentials.password,
        )
        result = await session.scalar(q)
        return result


security = HTTPBasicAuth()
