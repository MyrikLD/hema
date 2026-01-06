from hema.auth import security

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from hema.schemas.users import UserCreateResponseSchema, UserCreateSchema
from hema.services.user_service import UserService

from hema.db import db

router = APIRouter(prefix="/users", tags=["Users"])

@router.post('/registration', response_model=UserCreateResponseSchema)
async def user_registration(data : UserCreateSchema,
                            session: AsyncSession = Depends(db.get_db),):
    new_user = await UserService(session).create_user_profile(data)
    if not new_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="User with same phone number exists")
    return new_user