from pydantic import BaseModel, ConfigDict
from datetime import datetime


class PaymentUpdateShema(BaseModel):
    user_id: int
    payment: int | None
    comment: str | None

    model_config = ConfigDict(extra="forbid")


class PaymentResponseShema(PaymentUpdateShema):
    id: int
    timestamp: datetime
    trainer_id: int

    model_config = ConfigDict(from_attributes=True)
