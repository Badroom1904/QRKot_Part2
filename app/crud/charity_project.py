from typing import Optional

from app.crud.base import CRUDBase
from app.models import CharityProject


class CharityProjectCRUD(CRUDBase[CharityProject]):
    """CRUD для операций с целевыми проектами."""

    async def get_by_name(
        self,
        name: str,
        session,
    ) -> Optional[CharityProject]:
        """Получить проект по имени."""
        from sqlalchemy import select
        query = select(self.model).where(self.model.name == name)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_name_excluding_id(
        self,
        name: str,
        project_id: int,
        session,
    ) -> Optional[CharityProject]:
        """Получить проект по имени, исключая указанный ID."""
        from sqlalchemy import select
        query = select(self.model).where(
            self.model.name == name,
            self.model.id != project_id
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()


charity_project_crud = CharityProjectCRUD(CharityProject)