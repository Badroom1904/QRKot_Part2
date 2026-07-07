import httpx
from fastapi import HTTPException, status
from typing import Optional, Dict, Any

from app.core.config import settings


class YandexDiskClient:
    """Клиент для работы с API Яндекс Диска."""

    BASE_URL = "https://cloud-api.yandex.net/v1/disk"
    REPORTS_FOLDER = "QRKot Reports"

    def __init__(self, token: str):
        self.token = token
        self._session: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Асинхронный вход в контекстный менеджер."""
        self._session = httpx.AsyncClient(
            headers={
                "Authorization": f"OAuth {self.token}",
                "Accept": "application/json",
            },
            timeout=30.0,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный выход из контекстного менеджера."""
        if self._session:
            await self._session.aclose()
            self._session = None

    async def _request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """
        Выполняет HTTP-запрос к API Яндекс Диска.

        Args:
            method: HTTP-метод (GET, POST, PUT, DELETE)
            url: URL эндпоинта (относительно BASE_URL)
            params: Параметры запроса
            data: Данные для отправки
            files: Файлы для загрузки

        Returns:
            Response: Ответ от API

        Raises:
            HTTPException: При ошибке запроса
        """
        if not self._session:
            raise RuntimeError(
                "Session not initialized. Use 'async with' context manager."
            )

        full_url = f"{self.BASE_URL}{url}"
        response = await self._session.request(
            method=method,
            url=full_url,
            params=params,
            data=data,
            files=files,
        )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            # Для статуса 409 (конфликт) не выбрасываем исключение
            # (используется для проверки существования папки)
            if e.response.status_code == 409:
                return e.response
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Yandex Disk API error: {e.response.text}",
            )

        return response

    async def _create_folder(self, path: str) -> None:
        """
        Создаёт папку на Яндекс Диске.

        Args:
            path: Путь к папке

        Raises:
            HTTPException: При ошибке создания папки
        """
        response = await self._request(
            method="PUT",
            url="/resources",
            params={"path": path},
        )

        # Если папка уже существует (409) - игнорируем
        if response.status_code == 409:
            return

        if response.status_code != 201:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to create folder: {response.text}",
            )

    async def create_excel_file(self, filename: str) -> Dict[str, str]:
        """
        Получает ссылку для загрузки файла на Яндекс Диск.

        Args:
            filename: Имя файла

        Returns:
            Dict с ссылкой для загрузки и путём к файлу

        Raises:
            HTTPException: При ошибке получения ссылки
        """
        # Создаём папку, если её нет
        await self._create_folder(self.REPORTS_FOLDER)

        # Формируем путь к файлу
        file_path = f"{self.REPORTS_FOLDER}/{filename}"

        # Получаем ссылку для загрузки
        response = await self._request(
            method="GET",
            url="/resources/upload",
            params={"path": file_path, "overwrite": "true"},
        )

        data = response.json()
        upload_url = data.get("href")

        if not upload_url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to get upload URL",
            )

        return {"upload_url": upload_url, "file_path": file_path}

    async def upload_file(self, upload_url: str, file_content: bytes) -> None:
        """
        Загружает файл на Яндекс Диск по полученной ссылке.

        Args:
            upload_url: URL для загрузки
            file_content: Бинарное содержимое файла

        Raises:
            HTTPException: При ошибке загрузки
        """
        if not self._session:
            raise RuntimeError(
                "Session not initialized. Use 'async with' context manager."
            )

        response = await self._session.put(
            upload_url,
            content=file_content,
            timeout=60.0,
        )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to upload file: {e.response.text}",
            )

    async def publish_file(self, file_path: str) -> str:
        """
        Публикует файл и возвращает публичную ссылку.

        Args:
            file_path: Путь к файлу на Диске

        Returns:
            str: Публичная ссылка на файл

        Raises:
            HTTPException: При ошибке публикации
        """
        # Публикуем файл
        response = await self._request(
            method="PUT",
            url="/resources/publish",
            params={"path": file_path},
        )

        # Получаем публичную ссылку
        response = await self._request(
            method="GET",
            url="/resources",
            params={"path": file_path, "fields": "public_url"},
        )

        data = response.json()
        public_url = data.get("public_url")

        if not public_url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to get public URL",
            )

        return public_url


def get_yandex_client() -> YandexDiskClient:
    """
    Dependency для получения клиента Яндекс Диска.

    Returns:
        YandexDiskClient: Клиент Яндекс Диска

    Raises:
        HTTPException: Если токен не настроен (503)
    """
    token = settings.YANDEX_DISK_TOKEN
    if not token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Yandex Disk token not configured",
        )
    return YandexDiskClient(token)