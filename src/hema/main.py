from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path as PathLib

import uvicorn
from fastapi import FastAPI
from fastapi.params import Query
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

from hema.config import settings
from hema.db import db

api = FastAPI()

# Configure Jinja2 with templates directory
templates_dir = PathLib(__file__).parent.parent.parent / "templates"
jinja = Environment(loader=FileSystemLoader(templates_dir))


@asynccontextmanager
async def lifespan(api: FastAPI):
    db.init_db(settings.DB_URI)
    yield


@api.get("/health", include_in_schema=False)
def health_check():
    return {"message": "Alive"}


@api.get("/calendar", response_class=HTMLResponse)
@api.get("/calendar/{d}", response_class=HTMLResponse)
def calendar_current(day: date = Query(date.today())):
    """Redirect to current month calendar"""
    pass


if __name__ == "__main__":
    uvicorn.run(
        api,
        host="0.0.0.0",  # nosec
        port=8000,
        server_header=False,
    )
