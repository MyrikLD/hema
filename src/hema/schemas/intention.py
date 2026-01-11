from pydantic import BaseModel, ConfigDict


class VisitBaseSchema(BaseModel):

    user_id: int
    event_id: int

    model_config = ConfigDict(from_attributes=True)


class VisitResponseShema(VisitBaseSchema):
    id: int
