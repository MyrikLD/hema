from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PaymentSchema(BaseModel):
    user_id: int
    payment: int = Field(gt=0)
    comment: str | None = None

    model_config = ConfigDict(extra="forbid")


class PaymentResponseSchema(PaymentSchema):
    id: int
    timestamp: datetime
    trainer_id: int

    model_config = ConfigDict(from_attributes=True)
