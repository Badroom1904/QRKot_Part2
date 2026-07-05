from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import MetaData

from app.core.config import settings

metadata = MetaData()

Base = declarative_base(metadata=metadata)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncSession:
    """
    Генератор сессий для использования в эндпоинтах FastAPI.

    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
