from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class PaymentUpdateSchema(BaseModel):
    user_id: int
    payment: int = Field(gt=0)
    comment: str | None

    model_config = ConfigDict(extra="forbid")


class PaymentResponseSchema(PaymentUpdateSchema):
    id: int
    timestamp: datetime
    trainer_id: int

    model_config = ConfigDict(from_attributes=True)
