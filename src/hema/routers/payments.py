from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from hema.auth import TrainerIdDep, UserIdDep
from hema.db import SessionDep
from hema.schemas.payments import (
    PaymentResponseSchema,
    PaymentUpdateSchema,
)
from hema.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/balance", response_model=int)
async def get_user_balance(
    user_id: UserIdDep,
    session: SessionDep,
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
    session: SessionDep,
    trainer_id: UserIdDep,
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
    session: SessionDep,
    _: TrainerIdDep,
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
    user_id: UserIdDep,
    session: SessionDep,
) -> list:
    service = PaymentService(session)
    history = await service.get_user_payment_history(user_id=user_id)
    return history
