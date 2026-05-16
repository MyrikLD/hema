from datetime import time

from pydantic import BaseModel, ConfigDict, Field


class ScheduleEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    color: str
    weekday: int = Field(ge=0, le=6)  # 0=Monday … 6=Sunday
    time_start: time
    time_end: time
    trainer_id: int | None = None
    trainer_name: str | None = None
