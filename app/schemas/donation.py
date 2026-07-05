from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

from app.schemas.base import DonationBase, BaseModelMixin


class DonationCreate(DonationBase):
    """Схема для создания пожертвования."""

    comment: Optional[str] = Field(None, max_length=500)
    full_amount: int = Field(..., gt=0)

    class Config:
        """Конфигурация Pydantic."""

        extra = "forbid"

    @validator('full_amount')
    @classmethod
    def validate_full_amount(cls, value):
        """Валидация суммы пожертвования."""
        if value <= 0:
            raise ValueError('Сумма пожертвования должна быть больше 0')
        return value


class DonationDB(BaseModelMixin, DonationBase):
    """Схема для вывода пожертвования из БД (для суперпользователя)."""

    comment: Optional[str] = None
    full_amount: int
    user_id: int

    class Config:
        """Конфигурация Pydantic."""

        from_attributes = True


class DonationUserDB(BaseModel):
    """Схема для вывода пожертвования пользователю."""

    id: int
    comment: Optional[str] = None
    full_amount: int
    create_date: datetime

    class Config:
        """Конфигурация Pydantic."""

        from_attributes = True