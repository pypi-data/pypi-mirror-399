from collections.abc import Callable, AsyncGenerator
from typing import TypeVar

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from .repository import DatabaseRepository

Model = TypeVar("Model", bound=DeclarativeBase)


def get_repository(
    model: type[Model],
    session_dependency: Callable[[], AsyncGenerator[AsyncSession, None]],
) -> Callable[[AsyncSession], DatabaseRepository[Model]]:
    """
    Create a FastAPI dependency that provides a repository for the given model.

    Args:
        model: The SQLAlchemy model class
        session_dependency: A function that yields AsyncSession (from DatabaseSession.get_session)

    Returns:
        A dependency function for use with FastAPI's Depends()

    Example:
        from connect_db import DatabaseSession, get_repository
        from your_app.models import User

        db = DatabaseSession("postgresql+asyncpg://...")

        @app.get("/users")
        async def get_users(repo: DatabaseRepository[User] = Depends(get_repository(User, db.get_session))):
            return await repo.filter()
    """

    def func(session: AsyncSession = Depends(session_dependency)):
        return DatabaseRepository(model, session)

    return func
