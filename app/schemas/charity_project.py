from typing import Optional

from pydantic import BaseModel, Field, validator

from app.schemas.base import ProjectBase, BaseModelMixin


class CharityProjectCreate(ProjectBase):
    """Схема для создания нового проекта."""

    name: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10)
    full_amount: int = Field(..., gt=0)

    class Config:
        """Конфигурация Pydantic."""

        extra = "forbid"


class CharityProjectUpdate(BaseModel):
    """Схема для обновления проекта."""

    name: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=10)
    full_amount: Optional[int] = Field(None, gt=0)

    class Config:
        """Конфигурация Pydantic."""

        extra = "forbid"

    @validator('name')
    @classmethod
    def validate_name(cls, value):
        """Валидация названия при обновлении."""
        if value is not None:
            if not value or not value.strip():
                raise ValueError('Название не может быть пустым')
            return value.strip()
        return value

    @validator('description')
    @classmethod
    def validate_description(cls, value):
        """Валидация описания при обновлении."""
        if value is not None:
            if not value or not value.strip():
                raise ValueError('Описание не может быть пустым')
            return value.strip()
        return value

    @validator('full_amount')
    @classmethod
    def validate_full_amount(cls, value):
        """Валидация суммы при обновлении."""
        if value is not None and value <= 0:
            raise ValueError('Сумма должна быть больше 0')
        return value


class CharityProjectDB(BaseModelMixin, ProjectBase):
    """Схема для вывода проекта из БД."""

    name: str
    description: str
    full_amount: int

    class Config:
        """Конфигурация Pydantic."""

        from_attributes = True