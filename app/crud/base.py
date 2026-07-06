from typing import Generic, TypeVar, Type, Optional, List, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base

ModelType = TypeVar('ModelType', bound=Base)


class CRUDBase(Generic[ModelType]):
    """Базовый класс для CRUD операций."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> Optional[ModelType]:
        """Получить объект по ID."""
        query = select(self.model).where(self.model.id == obj_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        session: AsyncSession,
        *args,
        **kwargs,
    ) -> List[ModelType]:
        """Получить все объекты."""
        query = select(self.model)
        result = await session.execute(query)
        return result.scalars().all()

    async def create(
        self,
        obj_in: Any,
        session: AsyncSession,
        **kwargs,
    ) -> ModelType:
        """Создать новый объект."""
        obj_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in
        db_obj = self.model(**obj_data, **kwargs)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj: ModelType,
        obj_in: Any,
        session: AsyncSession,
    ) -> ModelType:
        """Обновить объект."""
        update_data = obj_in.dict(exclude_unset=True) if hasattr(
            obj_in, 'dict'
        ) else obj_in
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        db_obj: ModelType,
        session: AsyncSession,
    ) -> ModelType:
        """Удалить объект."""
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    async def get_open_projects(
        self,
        session: AsyncSession,
    ) -> List[ModelType]:
        """Получить все открытые проекты (для инвестирования)."""
        query = select(self.model).where(
            self.model.fully_invested.is_(False)
        ).order_by(self.model.create_date.asc())
        result = await session.execute(query)
        return result.scalars().all()

    async def get_open_donations(
        self,
        session: AsyncSession,
    ) -> List[ModelType]:
        """Получить все не полностью распределённые пожертвования."""
        query = select(self.model).where(
            self.model.fully_invested.is_(False)
        ).order_by(self.model.create_date.asc())
        result = await session.execute(query)
        return result.scalars().all()