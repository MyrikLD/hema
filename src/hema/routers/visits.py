from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from hema.auth import oauth2_scheme
from hema.db import db
from hema.schemas.visits import VisitResponse
from hema.services.visit_service import VisitService

router = APIRouter(prefix="/api/visits", tags=["Visits"])


@router.get("/me", response_model=list[VisitResponse])
async def get_my_visits(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(oauth2_scheme),
):
    service = VisitService(session)
    return await service.get_user_visits(user_id, limit, offset)
