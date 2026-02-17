from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VisitResponse(BaseModel):
    timestamp: datetime
    uid: str
    user_id: int | None
    event_id: int | None
    event_name: str | None = None
    event_color: str | None = None

    model_config = ConfigDict(from_attributes=True)
