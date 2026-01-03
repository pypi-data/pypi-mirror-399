"""
connect-db: Generic async database repository for SQLAlchemy and FastAPI.

Example usage:
    from connect_db import DatabaseSession, DatabaseRepository, get_repository
    from fastapi import Depends
    from your_app.models import User, Base

    # Initialize the database session manager
    db = DatabaseSession("postgresql+asyncpg://user:pass@host/db")

    # Use in FastAPI routes
    @app.get("/users")
    async def list_users(
        repo: DatabaseRepository[User] = Depends(get_repository(User, db.get_session))
    ):
        return await repo.filter()
"""

from .session import DatabaseSession, create_session_dependency
from .repository import DatabaseRepository
from .dependencies import get_repository

__all__ = [
    "DatabaseSession",
    "DatabaseRepository",
    "get_repository",
    "create_session_dependency",
]

__version__ = "0.1.0"
