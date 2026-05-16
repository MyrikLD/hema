from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm

from hema.auth import UserIdDep, create_jwt_token, oauth2_scheme, verify_password
from hema.db import SessionDep
from hema.schemas.users import (
    AuthResponseModel,
    UserCreateSchema,
    UserProfileUpdateShema,
    UserResponseSchema,
)
from hema.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/registration", response_model=UserResponseSchema)
async def user_registration(
    data: UserCreateSchema,
    session: SessionDep,
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
    user_id: UserIdDep,
    session: SessionDep,
):
    service = UserService(session)
    user_profile = await service.get_by_id(user_id)
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_profile


@router.patch("/", response_model=UserResponseSchema)
async def update_user_profile(
    user_id: UserIdDep,
    update_data: UserProfileUpdateShema,
    session: SessionDep,
):
    service = UserService(session)
    user_profile = await service.update_user_profile(user_id=user_id, update_data=update_data)
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_profile


@router.post("/login", response_model=AuthResponseModel)
async def user_loggin_in(
    data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> dict:
    service = UserService(session)

    user = await service.get_by_username(username=data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    password_check = verify_password(data.password, user["password"])
    if not password_check:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password are invalid")

    token_payload = {"user_id": user["id"]}
    token = create_jwt_token(data=token_payload)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/qr")
async def get_qr(
    user_id: UserIdDep,
    session: SessionDep,
):
    service = UserService(session)
    qr = service.qr_gen(user_id=user_id)
    return Response(content=qr, media_type="image/svg+xml")


@router.get(
    "/{user_id}",
    response_model=UserResponseSchema,
    dependencies=[Depends(oauth2_scheme.trainer)],
)
async def get_user(
    user_id: int,
    session: SessionDep,
):
    user = await UserService(session).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
