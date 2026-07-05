from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_async_session
from app.core.dependencies import current_superuser
from app.models import CharityProject, User
from app.schemas import (
    CharityProjectCreate,
    CharityProjectUpdate,
    CharityProjectDB,
)
from app.services import invest_free_donations_to_project

router = APIRouter()


@router.get(
    "/",
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True,
    summary="Получить список всех проектов",
    description="Возвращает список всех целевых проектов в Фонде. "
                "Доступно всем пользователям.",
)
async def get_all_projects(
    session: AsyncSession = Depends(get_async_session),
) -> List[CharityProjectDB]:
    """Получить все проекты (доступно всем)."""
    query = select(CharityProject).order_by(CharityProject.create_date.asc())
    result = await session.execute(query)
    return result.scalars().all()


@router.post(
    "/",
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="Создать новый проект",
    description="Создаёт новый целевой проект и автоматически распределяет "
                "в него все свободные пожертвования. "
                "Доступно только суперпользователям.",
)
async def create_project(
    project_in: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser),
) -> CharityProjectDB:
    """Создать новый проект (только для суперпользователей)."""
    query = select(CharityProject).where(
        CharityProject.name == project_in.name
    )
    result = await session.execute(query)
    existing_project = result.scalar_one_or_none()

    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Проект с таким названием уже существует",
        )

    new_project = CharityProject(**project_in.dict())
    session.add(new_project)

    await invest_free_donations_to_project(session, new_project)

    await session.commit()
    await session.refresh(new_project)

    return new_project


@router.patch(
    "/{project_id}",
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    summary="Обновить проект",
    description="Обновляет данные существующего проекта. "
                "Доступно только суперпользователям.",
)
async def update_project(
    project_id: int,
    project_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser),
) -> CharityProjectDB:
    """Обновить проект (только для суперпользователей)."""
    query = select(CharityProject).where(CharityProject.id == project_id)
    result = await session.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден",
        )

    if project.fully_invested:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Закрытый проект нельзя редактировать",
        )

    if project_in.name is not None:
        query = select(CharityProject).where(
            CharityProject.name == project_in.name,
            CharityProject.id != project_id
        )
        result = await session.execute(query)
        existing_project = result.scalar_one_or_none()

        if existing_project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Проект с таким названием уже существует",
            )

    if project_in.full_amount is not None:
        if project_in.full_amount < project.invested_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Новая требуемая сумма не может быть меньше "
                       "уже инвестированной",
            )
        if project_in.full_amount == project.invested_amount:
            project.fully_invested = True
            project.close_date = datetime.now()

    update_data = project_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    await session.commit()
    await session.refresh(project)

    return project


@router.delete(
    "/{project_id}",
    response_model=CharityProjectDB,
    summary="Удалить проект",
    description="Удаляет существующий проект из базы данных. "
                "Доступно только суперпользователям. "
                "Нельзя удалить проект, в который уже инвестировали.",
)
async def delete_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser),
) -> CharityProjectDB:
    """Удалить проект (только для суперпользователей)."""
    query = select(CharityProject).where(CharityProject.id == project_id)
    result = await session.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден",
        )

    if project.invested_amount > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить проект, в который уже инвестировали",
        )

    await session.delete(project)
    await session.commit()

    return project