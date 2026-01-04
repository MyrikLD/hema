from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path as PathLib

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Path, Query
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

from hema.auth import security
from hema.config import settings
from hema.db import db
from hema.routers import events
from hema.services.calendar_service import CalendarService


@asynccontextmanager
async def lifespan(api: FastAPI):
    db.init_db(settings.DB_URI)
    yield


api = FastAPI(
    lifespan=lifespan,
    title="HEMA Training Calendar",
    description="Training attendance tracking system for Historical European Martial Arts",
    version="0.1.0",
)

# Register API routers
api.include_router(events.router)

# Configure Jinja2 with templates directory
templates_dir = PathLib(__file__).parent.parent.parent / "templates"
jinja = Environment(loader=FileSystemLoader(templates_dir))


@api.get("/health", include_in_schema=False)
def health_check():
    return {"message": "Alive"}


@api.get("/calendar", response_class=HTMLResponse)
async def calendar_current(
    db_session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(security),
):
    """Show current month calendar."""
    today = date.today()
    data = await CalendarService.get_month_data(db_session, today.year, today.month)
    template = jinja.get_template("calendar.xhtml")
    return template.render(**data)


@api.get("/calendar/{year}/{month}", response_class=HTMLResponse)
async def calendar_month(
    year: int = Path(gt=2025, le=2100),
    month: int = Path(ge=1, le=12),
    db_session: AsyncSession = Depends(db.get_db),
    user_id: int = Depends(security),
):
    """Show specific month calendar."""
    try:
        data = await CalendarService.get_month_data(db_session, year, month)
        template = jinja.get_template("calendar.xhtml")
        return template.render(**data)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error rendering calendar: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        api,
        host="0.0.0.0",  # nosec
        port=8000,
        server_header=False,
    )
