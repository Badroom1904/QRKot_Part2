from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.dependencies import current_superuser
from app.models import CharityProject, User
from app.schemas import (
    CharityProjectCreate,
    CharityProjectUpdate,
    CharityProjectDB,
)
from app.services import invest_free_donations_to_project
from app.crud import charity_project_crud

router = APIRouter()


@router.get(
    "/",
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True,
    summary="Получить список всех проектов",
    description="Возвращает список всех целевых проектов в Фонде.",
)
async def get_all_projects(
    session: AsyncSession = Depends(get_async_session),
) -> List[CharityProjectDB]:
    """Получить все проекты (доступно всем)."""
    return await charity_project_crud.get_all(session)


@router.post(
    "/",
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="Создать новый проект",
    description="Создаёт новый целевой проект и автоматически распределяет "
                "в него все свободные пожертвования.",
)
async def create_project(
    project_in: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser),
) -> CharityProjectDB:
    """Создать новый проект (только для суперпользователей)."""
    existing_project = await charity_project_crud.get_by_name(
        project_in.name, session
    )

    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Проект с таким названием уже существует",
        )

    new_project = await charity_project_crud.create(
        project_in, session
    )

    await invest_free_donations_to_project(session, new_project)

    await session.commit()
    await session.refresh(new_project)

    return new_project


@router.patch(
    "/{project_id}",
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    summary="Обновить проект",
    description="Обновляет данные существующего проекта.",
)
async def update_project(
    project_id: int,
    project_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser),
) -> CharityProjectDB:
    """Обновить проект (только для суперпользователей)."""
    project = await charity_project_crud.get(project_id, session)

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
        existing_project = await charity_project_crud.get_by_name_excluding_id(
            project_in.name, project_id, session
        )

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

    updated_project = await charity_project_crud.update(
        project, project_in, session
    )

    return updated_project


@router.delete(
    "/{project_id}",
    response_model=CharityProjectDB,
    summary="Удалить проект",
    description="Удаляет существующий проект из базы данных.",
)
async def delete_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser),
) -> CharityProjectDB:
    """Удалить проект (только для суперпользователей)."""
    project = await charity_project_crud.get(project_id, session)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден",
        )

    if project.fully_invested:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить закрытый проект",
        )

    if project.invested_amount > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить проект, в который уже инвестировали",
        )

    return await charity_project_crud.delete(project, session)