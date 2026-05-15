from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from hema.auth import oauth2_scheme
from hema.db import db
from hema.schemas.visits import VisitResponse, VisitMarkPostSchema, VisitMarkResponseSchema
from hema.services.visit_service import VisitService

router = APIRouter(prefix="/visits", tags=["Visits"])


@router.get("/me", response_model=list[VisitResponse])
async def get_my_visits(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(oauth2_scheme),
):
    service = VisitService(session)
    return await service.get_user_visits(user_id, limit, offset)


@router.post("/qr_visit", response_model=VisitMarkResponseSchema)
async def post_visit(
    data: VisitMarkPostSchema,
    session: AsyncSession = Depends(db.get_db),
    trainer_id: int = Depends(oauth2_scheme),
) -> dict:
    visit_service = VisitService(session)
    visit_data = await visit_service.mark_visit(data=data, trainer_id=trainer_id)
    if visit_data["status"] == "forbidden":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your event")
    return visit_data
