from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from hema.config import settings
from hema.db import db
from hema.routers import (
    calendar_router,
    calendar_api_router,
    esp_router,
    events_router,
    users_router,
    weekly_events_router,
)


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

# Add CORS middleware
api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
api.mount("/static", StaticFiles(directory=str(settings.ROOT / "static")), name="static")

# Register API routers
api.include_router(calendar_router)
api.include_router(calendar_api_router)
api.include_router(events_router)
api.include_router(weekly_events_router)
api.include_router(users_router)
api.include_router(esp_router)


@api.get("/health", include_in_schema=False)
def health_check():
    return {"message": "Alive"}


if __name__ == "__main__":
    uvicorn.run(
        api,
        host="0.0.0.0",  # nosec
        port=8000,
        server_header=False,
    )
