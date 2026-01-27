from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from hema.auth import create_jwt_token, oauth2_scheme, verify_password
from hema.db import db
from hema.schemas.users import (
    UserCreateSchema,
    UserProfileUpdateShema,
    UserResponseSchema,
)
from hema.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("/registration", response_model=UserResponseSchema)
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


@router.get("/me", response_model=UserResponseSchema)
async def get_user_profile(
    session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(oauth2_scheme),
):
    service = UserService(session)
    user_profile = await service.get(user_id=user_id)
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_profile


@router.patch("/", response_model=UserResponseSchema)
async def update_user_profile(
    update_data: UserProfileUpdateShema,
    session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(oauth2_scheme),
):
    service = UserService(session)
    user_profile = await service.update_user_profile(user_id=user_id, update_data=update_data)
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_profile


@router.patch("/attach_uid", response_model=UserResponseSchema)
async def update_user_profile(
    uid: str = Body(..., embed=True),
    session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(oauth2_scheme),
):
    service = UserService(session)
    user_profile = await service.attach_uid(user_id=user_id, uid=uid)
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_profile


@router.post("/login")
async def user_loggin_in(
    data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(db.get_db),
) -> dict | None:
    service = UserService(session)

    user = await service.get_by_username(username=data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    password_check = verify_password(data.password, user["password"])
    if not password_check:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Phone or Password are invalid"
        )

    token_payload = {"user_id": user["id"]}
    token = create_jwt_token(data=token_payload)
    return {"access_token": token, "token_type": "bearer"}
