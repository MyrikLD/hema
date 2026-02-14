from pydantic import BaseModel, ConfigDict
from datetime import datetime


class DepositUpdateShema(BaseModel):
    user_id: int | None
    payment: int | None
    comment: str | None

    model_config = ConfigDict(extra="forbid")


class DepositUpdateResponseShema(DepositUpdateShema):
    id: int
    timestamp: datetime
    trainer_id: int

    model_config = ConfigDict(from_attributes=True)


class BalanceResponse(BaseModel):
    balance: int

    model_config = ConfigDict(from_attributes=True)


class DeleteUserPayment(BaseModel):
    id: int

    model_config = ConfigDict(extra="forbid")
