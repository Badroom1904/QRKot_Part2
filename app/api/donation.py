from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_async_session
from app.core.dependencies import current_user, current_superuser
from app.models import Donation, User
from app.schemas import (
    DonationCreate,
    DonationDB,
    DonationUserDB,
)
from app.services import invest_donations_to_projects

router = APIRouter()


@router.get(
    "/",
    response_model=List[DonationDB],
    response_model_exclude_none=True,
    summary="Получить список всех пожертвований",
    description="Возвращает список всех пожертвований в Фонде. "
                "Доступно только суперпользователям.",
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser),
) -> List[DonationDB]:
    """Получить все пожертвования (только для суперпользователей)."""
    query = select(Donation).order_by(Donation.create_date.asc())
    result = await session.execute(query)
    return result.scalars().all()


@router.post(
    "/",
    response_model=DonationUserDB,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="Сделать пожертвование",
    description="Создаёт новое пожертвование и автоматически распределяет "
                "его по открытым проектам. "
                "Доступно только авторизованным пользователям.",
)
async def create_donation(
    donation_in: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
) -> DonationUserDB:
    """Создать новое пожертвование (только для авторизованных)."""
    new_donation = Donation(
        **donation_in.dict(),
        user_id=user.id
    )
    session.add(new_donation)

    await invest_donations_to_projects(session, new_donation)

    await session.commit()
    await session.refresh(new_donation)

    return new_donation


@router.get(
    "/my",
    response_model=List[DonationUserDB],
    response_model_exclude_none=True,
    summary="Получить мои пожертвования",
    description="Возвращает список пожертвований текущего пользователя. "
                "Доступно только авторизованным пользователям.",
)
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
) -> List[DonationUserDB]:
    """Получить пожертвования текущего пользователя."""
    query = select(Donation).where(
        Donation.user_id == user.id
    ).order_by(Donation.create_date.asc())
    result = await session.execute(query)
    return result.scalars().all()