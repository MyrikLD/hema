"""API routes for Event management."""

import csv
from datetime import datetime

import sqlalchemy as sa
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from hema.db import db
from hema.models import VisitModel
from hema.services.esp import EventMapper, UserMapper

router = APIRouter(prefix="/api/esp", tags=["ESP"])


@router.post("")
async def receive_sync(
    request: Request,
    session: AsyncSession = Depends(db.get_db, scope="function"),
):
    file = await request.body()
    reader = csv.DictReader(file.decode().splitlines())
    reader.fieldnames = ["timestamp", "uid"]
    items = [
        {
            "timestamp": datetime.fromtimestamp(int(i["timestamp"])),
            "uid": i["uid"],
        }
        for i in reader
    ]
    q = VisitModel.__table__.delete().where(
        sa.and_(
            VisitModel.timestamp == sa.bindparam("timestamp"),
            VisitModel.uid == sa.bindparam("uid"),
        )
    )
    await session.execute(q, items)

    uids = {row["uid"] for row in items}
    um = UserMapper()
    await um.load(session, uids)

    timestamps = {row["timestamp"] for row in items}
    start = min(timestamps)
    end = max(timestamps)

    em = EventMapper()
    await em.load(session, start, end)

    values = []
    for item in items:
        values.append(
            {
                VisitModel.timestamp.name: item["timestamp"],
                VisitModel.uid.name: item["uid"],
                VisitModel.user_id.name: um.get(item["uid"]),
                VisitModel.event_id.name: em.get(item["timestamp"]),
            }
        )

    q = sa.insert(VisitModel).values(values)
    await session.execute(q)


@router.get("/available", response_model=dict[str, datetime])
async def get_available_uids(
    session: AsyncSession = Depends(db.get_db),
):
    q = (
        sa.select(VisitModel.uid, func.max(VisitModel.timestamp))
        .where(VisitModel.user_id.is_(None))
        .group_by(VisitModel.uid)
        .order_by(func.max(VisitModel.timestamp))
    )
    return dict((await session.execute(q)).all())
