from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class BaseModelMixin(BaseModel):
    """Базовый класс для всех схем с общими полями."""

    id: int
    create_date: datetime
    close_date: Optional[datetime] = None
    fully_invested: bool = False
    invested_amount: int = 0

    class Config:
        """Конфигурация Pydantic."""

        from_attributes = True


class ProjectBase(BaseModel):
    """Базовая схема для проекта."""

    name: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10)
    full_amount: int = Field(..., gt=0)

    @validator('name')
    @classmethod
    def validate_name(cls, value):
        """Дополнительная валидация названия."""
        if not value or not value.strip():
            raise ValueError('Название не может быть пустым')
        return value.strip()

    @validator('description')
    @classmethod
    def validate_description(cls, value):
        """Дополнительная валидация описания."""
        if not value or not value.strip():
            raise ValueError('Описание не может быть пустым')
        return value.strip()

    @validator('full_amount')
    @classmethod
    def validate_full_amount(cls, value):
        """Валидация суммы."""
        if value <= 0:
            raise ValueError('Сумма должна быть больше 0')
        return value


class DonationBase(BaseModel):
    """Базовая схема для пожертвования."""

    comment: Optional[str] = Field(None, max_length=500)
    full_amount: int = Field(..., gt=0)

    @validator('full_amount')
    @classmethod
    def validate_full_amount(cls, value):
        """Валидация суммы пожертвования."""
        if value <= 0:
            raise ValueError('Сумма пожертвования должна быть больше 0')
        return value