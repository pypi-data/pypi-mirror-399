from typing import Generic, TypeVar, Any
import uuid

from fastapi import HTTPException, status
from sqlalchemy import BinaryExpression, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, DBAPIError
from sqlalchemy.orm import DeclarativeBase

import logging

log = logging.getLogger(__name__)

Model = TypeVar("Model", bound=DeclarativeBase)


class DatabaseRepository(Generic[Model]):
    """Generic repository for performing async database queries on SQLAlchemy models."""

    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def create(self, data: dict[str, Any]) -> Model:
        """Create a new record."""
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def create_children(self, data: dict[str, Any], children: list[dict] | None = None) -> Model:
        """Create a record with nested child relationships."""
        instance = self.model(**data)
        if children:
            for child in children:
                child_model = child["model"]
                child_data = child["data"]
                attr_name = child["attr_name"]

                if isinstance(child_data, list):
                    for list_item in child_data:
                        obj = child_model(**list_item)
                        getattr(instance, attr_name).append(obj)
                else:
                    obj = child_model(**child_data)
                    setattr(instance, attr_name, obj)

        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def create_many(self, data: list[dict[str, Any]], return_models: bool = False) -> list[Model] | bool:
        """Create multiple records."""
        instances = [self.model(**d) for d in data]
        self.session.add_all(instances)
        await self.session.commit()

        if not return_models:
            return True

        for obj in instances:
            await self.session.refresh(obj)

        return instances

    async def get(self, id: uuid.UUID) -> Model | None:
        """Get a record by ID."""
        return await self.session.get(self.model, id)

    async def get_by_column(
        self,
        column: str,
        value: list[str] | list[int] | list[uuid.UUID],
    ) -> list[Model]:
        """Get records by column value(s)."""
        if len(value) == 1:
            query = select(self.model).where(getattr(self.model, column) == value[0])
        else:
            query = select(self.model).where(getattr(self.model, column).in_(value))
        rows = await self.session.execute(query)
        return list(rows.unique().scalars().all())

    async def filter(self, *expressions: BinaryExpression) -> list[Model]:
        """Filter records by SQLAlchemy expressions."""
        query = select(self.model)
        if expressions:
            query = query.where(*expressions)
        return list(await self.session.scalars(query))

    async def delete(
        self,
        value: list[str] | list[int] | list[uuid.UUID],
        column: str = "id",
    ) -> int:
        """Delete records by column value(s). Returns count of deleted rows."""
        if len(value) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide at least one value",
            )
        if len(value) == 1:
            query = delete(self.model).where(getattr(self.model, column) == value[0])
        else:
            query = delete(self.model).where(getattr(self.model, column).in_(value))

        try:
            rows = await self.session.execute(query)
        except (SQLAlchemyError, DBAPIError) as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc.__dict__.get("orig", str(exc))),
            )

        await self.session.commit()
        return rows.rowcount

    async def update(self, id: uuid.UUID, data: dict[str, Any]) -> Model:
        """Update a record by ID."""
        db_model = await self.session.get(self.model, id)

        if db_model is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} does not exist",
            )

        for key, value in data.items():
            setattr(db_model, key, value)
            self.session.add(db_model)

        await self.session.commit()
        await self.session.refresh(db_model)
        return db_model
