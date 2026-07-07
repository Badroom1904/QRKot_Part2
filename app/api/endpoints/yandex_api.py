from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_async_session
from app.core.dependencies import current_superuser
from app.core.yandex_client import get_yandex_client, YandexDiskClient
from app.models import CharityProject, User
from app.services.yandex_api import create_simple_report
from app.crud import charity_project_crud

router = APIRouter()


@router.post(
    "/report",
    response_model=str,
    summary="Создать отчёт о проектах",
    description="Создаёт Excel-отчёт о закрытых проектах, "
                "загружает его на Яндекс Диск и возвращает публичную ссылку. "
                "Доступно только суперпользователям.",
)
async def create_report(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser),
) -> str:
    """
    Создаёт Excel-отчёт о закрытых проектах.

    Returns:
        str: Публичная ссылка на файл на Яндекс Диске
    """
    # Получаем закрытые проекты
    closed_projects = await charity_project_crud.get_closed_projects(
        session
    )

    if not closed_projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No closed projects found for report",
        )

    # Формируем имя файла
    from datetime import datetime
    from app.core.config import settings

    timestamp = datetime.now().strftime(settings.REPORT_FORMAT)
    filename = f"report_{timestamp}.xlsx"

    try:
        # Используем клиент Яндекс Диска через контекстный менеджер
        yandex_client = get_yandex_client()
        async with yandex_client as client:
            public_url = await create_simple_report(
                client,
                filename,
                closed_projects,
            )
        return public_url
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create report: {str(e)}",
        )