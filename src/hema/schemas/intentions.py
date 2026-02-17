from pydantic import BaseModel, ConfigDict


class IntentionCreate(BaseModel):
    event_id: int

    model_config = ConfigDict(extra="forbid")


class IntentionResponse(BaseModel):
    id: int
    user_id: int
    event_id: int

    model_config = ConfigDict(from_attributes=True)
