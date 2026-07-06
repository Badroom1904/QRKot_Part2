from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation
from app.crud import charity_project_crud, donation_crud


async def invest_donations_to_projects(
    session: AsyncSession,
    donation: Donation
) -> None:
    """Распределяет пожертвование по открытым проектам.

    Алгоритм:
    1. Находит все открытые проекты (fully_invested=False),
       отсортированные по дате создания (самые старые первыми)
    2. Распределяет сумму пожертвования по проектам по очереди
    3. Закрывает проекты, которые набрали нужную сумму
    4. Закрывает пожертвование, если все деньги распределены

    Args:
        session: Асинхронная сессия SQLAlchemy
        donation: Объект пожертвования для распределения
    """

    open_projects = await charity_project_crud.get_open_projects(session)

    if not open_projects:
        return

    invested_amount = donation.invested_amount or 0
    remaining_amount = donation.full_amount - invested_amount

    if remaining_amount <= 0:
        return

    for project in open_projects:
        project_invested = project.invested_amount or 0
        needed_amount = project.full_amount - project_invested

        if needed_amount <= 0:
            continue

        if remaining_amount >= needed_amount:
            invest_amount = needed_amount
            project.invested_amount = project.full_amount
            project.fully_invested = True
            project.close_date = datetime.now()
        else:
            invest_amount = remaining_amount
            project.invested_amount = (
                project.invested_amount or 0
            ) + invest_amount

        donation.invested_amount = (
            donation.invested_amount or 0
        ) + invest_amount
        remaining_amount -= invest_amount

        if donation.invested_amount >= donation.full_amount:
            donation.fully_invested = True
            donation.close_date = datetime.now()
            break

    session.add(donation)
    for project in open_projects:
        session.add(project)


async def invest_free_donations_to_project(
    session: AsyncSession,
    project: CharityProject
) -> None:
    """Распределяет свободные пожертвования в новый проект.

    Алгоритм:
    1. Находит все пожертвования с нераспределёнными средствами
       (fully_invested=False), отсортированные по дате создания
    2. Распределяет их суммы в новый проект по очереди
    3. Закрывает пожертвования, которые полностью распределены
    4. Закрывает проект, если набрана нужная сумма

    Args:
        session: Асинхронная сессия SQLAlchemy
        project: Объект проекта для инвестирования
    """

    open_donations = await donation_crud.get_open_donations(session)

    if not open_donations:
        return

    invested_amount = project.invested_amount or 0
    needed_amount = project.full_amount - invested_amount

    if needed_amount <= 0:
        return

    for donation in open_donations:

        donation_invested = donation.invested_amount or 0
        remaining_donation_amount = donation.full_amount - donation_invested

        if remaining_donation_amount <= 0:
            continue

        if remaining_donation_amount >= needed_amount:
            invest_amount = needed_amount
            project.invested_amount = project.full_amount
            project.fully_invested = True
            project.close_date = datetime.now()
        else:
            invest_amount = remaining_donation_amount
            project.invested_amount = (
                project.invested_amount or 0
            ) + invest_amount

        donation.invested_amount = (
            donation.invested_amount or 0
        ) + invest_amount
        needed_amount -= invest_amount

        if donation.invested_amount >= donation.full_amount:
            donation.fully_invested = True
            donation.close_date = datetime.now()

        if project.fully_invested:
            break

    session.add(project)
    for donation in open_donations:
        session.add(donation)