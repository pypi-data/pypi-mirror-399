from collections.abc import AsyncGenerator
from typing import Callable

from sqlalchemy import exc
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)

import logging

log = logging.getLogger(__name__)


class DatabaseSession:
    """Manages async database sessions with configurable connection."""

    def __init__(self, database_url: str, echo: bool = False):
        """
        Initialize the database session manager.

        Args:
            database_url: The async database URL (e.g., postgresql+asyncpg://...)
            echo: Whether to log SQL statements
        """
        self._database_url = database_url
        self._echo = echo
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            self._engine = create_async_engine(self._database_url, echo=self._echo)
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(self.engine)
        return self._session_factory

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Yield a database session with automatic commit/rollback handling."""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except exc.SQLAlchemyError:
                await session.rollback()
                raise

    def get_session_dependency(self) -> Callable[[], AsyncGenerator[AsyncSession, None]]:
        """Return a FastAPI-compatible dependency function."""
        return self.get_session


# Convenience function for simple use cases
def create_session_dependency(database_url: str, echo: bool = False) -> Callable[[], AsyncGenerator[AsyncSession, None]]:
    """
    Create a FastAPI dependency for database sessions.

    Args:
        database_url: The async database URL
        echo: Whether to log SQL statements

    Returns:
        A dependency function for use with FastAPI's Depends()
    """
    db = DatabaseSession(database_url, echo)
    return db.get_session
