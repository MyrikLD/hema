from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hema.db import db
from hema.auth import oauth2_scheme
from hema.schemas.payments import (
    PaymentResponseSchema,
    PaymentUpdateSchema,
)
from hema.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/balance", response_model=int)
async def get_user_balance(
    user_id: int = Depends(oauth2_scheme), session: AsyncSession = Depends(db.get_db)
):
    service = PaymentService(session)
    try:
        db_data = await service.get_user_balance(user_id)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No balance changes"
        ) from e
    return db_data


@router.post("/balance", response_model=PaymentResponseSchema)
async def update_user_balance(
    data: PaymentUpdateSchema,
    session: AsyncSession = Depends(db.get_db),
    trainer_id: int = Depends(oauth2_scheme),
):
    service = PaymentService(session)
    try:
        update = await service.update_user_deposit(payment_data=data, trainer_id=trainer_id)
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only for trainer") from e
    return update


@router.delete("/payment/{payment_id}", response_model=int)
async def delete_user_payment(
    payment_id: int,
    trainer_id: int = Depends(oauth2_scheme),
    session: AsyncSession = Depends(db.get_db),
) -> int | None:
    service = PaymentService(session)
    try:
        delete_payment = await service.delete_user_payment(payment_id)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
        ) from e
    return delete_payment


@router.get("/payment_history", response_model=list[PaymentResponseSchema])
async def get_user_payment_history(
    user_id: int = Depends(oauth2_scheme), session: AsyncSession = Depends(db.get_db)
) -> list:
    service = PaymentService(session)
    history = await service.get_user_payment_history(user_id=user_id)
    return history
