"""Basic authentication dependencies for API routes."""

import sqlalchemy as sa
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from hema.db import db
from hema.models import UserModel


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
