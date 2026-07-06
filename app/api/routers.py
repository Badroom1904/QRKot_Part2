"""Модуль для объявления всех роутеров API."""

from fastapi import APIRouter

from app.api.charity_project import router as charity_project_router
from app.api.donation import router as donation_router

router = APIRouter()

router.include_router(
    charity_project_router,
    prefix="/charity_project",
    tags=["Целевые проекты"],
)

router.include_router(
    donation_router,
    prefix="/donation",
    tags=["Пожертвования"],
)