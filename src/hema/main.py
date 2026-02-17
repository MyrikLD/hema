from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from hema.config import settings
from hema.db import db
from hema.routers import (
    calendar_router,
    esp_router,
    events_router,
    intentions_router,
    users_router,
    visits_router,
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

# CORS middleware for frontend dev server
api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
api.mount("/static", StaticFiles(directory=str(settings.ROOT / "static")), name="static")

# Serve frontend build assets if available
FRONTEND_DIST = settings.ROOT / "frontend" / "dist"
if FRONTEND_DIST.exists():
    api.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="frontend-assets")

# Register API routers
api.include_router(calendar_router)
api.include_router(events_router)
api.include_router(weekly_events_router)
api.include_router(users_router)
api.include_router(esp_router)
api.include_router(intentions_router)
api.include_router(visits_router)


@api.get("/health", include_in_schema=False)
def health_check():
    return {"message": "Alive"}


# SPA fallback: serve index.html for non-API routes
@api.get("/{path:path}", include_in_schema=False)
async def spa_fallback(path: str):
    index = FRONTEND_DIST / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"detail": "Frontend not built. Run: cd frontend && npm run build"}


if __name__ == "__main__":
    uvicorn.run(
        api,
        host="0.0.0.0",  # nosec
        port=8000,
        server_header=False,
    )
