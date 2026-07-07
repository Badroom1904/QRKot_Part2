from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject


class CharityProjectCRUD(CRUDBase[CharityProject]):
    """CRUD для операций с целевыми проектами."""

    async def get_by_name(
        self,
        name: str,
        session: AsyncSession,
    ) -> Optional[CharityProject]:
        """Получить проект по имени."""
        query = select(self.model).where(self.model.name == name)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_name_excluding_id(
        self,
        name: str,
        project_id: int,
        session: AsyncSession,
    ) -> Optional[CharityProject]:
        """Получить проект по имени, исключая указанный ID."""
        query = select(self.model).where(
            self.model.name == name,
            self.model.id != project_id
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_closed_projects(
        self,
        session: AsyncSession,
    ) -> List[CharityProject]:
        """
        Получить все закрытые проекты,
        отсортированные по скорости сбора (от быстрых к медленным).
        """
        query = select(self.model).where(
            self.model.fully_invested.is_(True),
            self.model.close_date.is_not(None),
            self.model.create_date.is_not(None),
        ).order_by(
            (self.model.close_date - self.model.create_date).asc()
        )
        result = await session.execute(query)
        return result.scalars().all()


charity_project_crud = CharityProjectCRUD(CharityProject)