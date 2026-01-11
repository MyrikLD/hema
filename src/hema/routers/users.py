from hema.auth import security

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from hema.schemas.users import (
    UserCreateResponseSchema,
    UserCreateSchema,
    UserProfileUpdateShema,
)
from hema.services.user_service import UserService
from hema.auth import security
from hema.db import db

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/registration", response_model=UserCreateResponseSchema)
async def user_registration(
    data: UserCreateSchema,
    session: AsyncSession = Depends(db.get_db),
):
    new_user = await UserService(session).create_user_profile(data)
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with same phone number exists",
        )
    return new_user


@router.get("/", response_model=UserCreateResponseSchema)
async def get_user_profile(
    session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(security),
):
    service = UserService(session)
    user_profile = service.get_user_profile(user_id=user_id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user_profile


@router.patch("/", response_model=UserCreateResponseSchema)
async def update_user_profile(
    update_data: UserProfileUpdateShema,
    session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(security),
):
    service = UserService(session)
    user_profile = await service.update_user_profile(
        user_id=user_id, update_data=update_data
    )
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user_profile
