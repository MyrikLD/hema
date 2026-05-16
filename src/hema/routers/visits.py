from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from hema.auth import TrainerIdDep, UserIdDep
from hema.db import SessionDep
from hema.schemas.visits import VisitMarkPostSchema, VisitResponse
from hema.services.visit_service import VisitService

router = APIRouter(prefix="/visits", tags=["Visits"])


@router.get("/me", response_model=list[VisitResponse])
async def get_my_visits(
    session: SessionDep,
    user_id: UserIdDep,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
):
    service = VisitService(session)
    return await service.get_user_visits(user_id, limit, offset)


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
async def post_visit(
    data: VisitMarkPostSchema,
    session: SessionDep,
    trainer_id: TrainerIdDep,
):
    try:
        await VisitService(session).mark_visit(
            user_id=data.user_id,
            event_id=data.event_id,
            trainer_id=trainer_id,
        )
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already marked")
