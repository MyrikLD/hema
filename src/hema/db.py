import logging
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

from hema.config import settings


class Database:
    engine: AsyncEngine = None
    async_session: async_sessionmaker[AsyncSession] = None

    def __init__(self, database_url: str, echo: bool = False):
        self.engine = create_async_engine(
            database_url,
            echo=False,
            future=True,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
        )
        if echo:
            logging.getLogger("sqlalchemy.engine.Engine").handlers.clear()

        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def get_db(self) -> AsyncSession:
        async with self.async_session() as session, session.begin():
            yield session

    @asynccontextmanager
    async def context(self) -> AsyncSession:
        async with asynccontextmanager(self.get_db)() as session:
            yield session


# Create a single instance
db = Database(settings.DB_URI)
