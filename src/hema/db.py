import logging
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)


class Database:
    engine: AsyncEngine = None
    async_session: async_sessionmaker[AsyncSession] = None

    def init_db(self, database_url: str, echo: bool = False):
        self.engine = create_async_engine(
            database_url,
            echo=False,
            future=True,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
        )
        if echo:
            # Clear all sqlalchemy handlers
            logging.getLogger("sqlalchemy.engine.Engine").handlers.clear()

        # Create async session factory
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)

    # Dependency to get DB session
    async def get_db(self) -> AsyncSession:
        if self.async_session is None:
            raise Exception("Database not initialized")
        async with self.async_session() as session, session.begin():
            yield session

    @asynccontextmanager
    async def context(self) -> AsyncSession:
        async with asynccontextmanager(self.get_db)() as session:
            yield session


# Create a single instance
db = Database()
