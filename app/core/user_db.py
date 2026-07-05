from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.models import User


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """Получение базы данных пользователей."""
    yield SQLAlchemyUserDatabase(session, User)