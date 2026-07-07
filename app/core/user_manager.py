from typing import Optional

from fastapi import Depends
from fastapi_users import BaseUserManager, IntegerIDMixin, models
from fastapi_users.exceptions import InvalidPasswordException
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from app.models import User
from app.core.config import settings
from app.core.user_db import get_user_db


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """Менеджер пользователей для FastAPI Users."""

    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def validate_password(
        self,
        password: str,
        user: Optional[models.UP] = None,
    ) -> None:
        """Валидация пароля.

        Минимальная длина - 3 символа (как требует тест).
        """
        if len(password) < 3:
            raise InvalidPasswordException(
                reason="Password should be at least 3 characters"
            )
        return await super().validate_password(password, user)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> UserManager:
    """Получение менеджера пользователей."""
    return UserManager(user_db)