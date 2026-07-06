from app.crud.base import CRUDBase
from app.models import Donation


class DonationCRUD(CRUDBase[Donation]):
    """CRUD для операций с пожертвованиями."""

    async def get_by_user(
        self,
        user_id: int,
        session,
    ):
        """Получить все пожертвования пользователя."""
        from sqlalchemy import select
        query = select(self.model).where(
            self.model.user_id == user_id
        ).order_by(self.model.create_date.asc())
        result = await session.execute(query)
        return result.scalars().all()


donation_crud = DonationCRUD(Donation)