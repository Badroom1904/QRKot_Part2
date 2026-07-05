from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.auth import auth_backend, fastapi_users
from app.core.register_router import get_register_router
from app.core.user_manager import get_user_manager
from app.api import charity_project_router, donation_router
from app.schemas.user import UserRead, UserCreate, UserUpdate

app = FastAPI(
    title="QRKot - Благотворительный фонд поддержки котиков",
    description=(
        "API для управления целевыми проектами и пожертвованиями "
        "в фонде QRKot. Автоматическое инвестирование пожертвований "
        "в открытые проекты."
    ),
    version="2.0.0",
)

app.include_router(
    get_register_router(UserRead, UserCreate, get_user_manager),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

users_router = fastapi_users.get_users_router(UserRead, UserUpdate)
users_router.routes = [
    route for route in users_router.routes
    if route.name != "users:delete_user"
]

app.include_router(
    users_router,
    prefix="/users",
    tags=["users"],
)

app.include_router(
    charity_project_router,
    prefix="/charity_project",
    tags=["Целевые проекты"],
)

app.include_router(
    donation_router,
    prefix="/donation",
    tags=["Пожертвования"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Корневой эндпоинт для проверки работоспособности."""
    return {
        "message": "Добро пожаловать в QRKot API!",
        "docs": "/docs",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Эндпоинт для проверки состояния сервиса."""
    return {"status": "healthy"}