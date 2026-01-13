"""API routes for Event management."""

import csv
from datetime import datetime
from typing import Annotated

import sqlalchemy as sa
from fastapi import APIRouter, Depends, File
from sqlalchemy.ext.asyncio import AsyncSession

from hema.db import db
from hema.models import VisitModel
from hema.services.esp import EventMapper, UserMapper

router = APIRouter(prefix="/api/esp", tags=["ESP"])


@router.post("")
async def receive_sync(
    file: Annotated[bytes, File()],
    session: AsyncSession = Depends(db.get_db, scope="function"),
):
    reader = csv.DictReader(file.decode().splitlines())
    reader.fieldnames = ["timestamp", "uid"]
    items = [
        {
            "timestamp": datetime.fromtimestamp(int(i["timestamp"])),
            "uid": i["uid"],
        }
        for i in reader
    ]

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
