from datetime import timedelta
from typing import List
from io import BytesIO
import xlsxwriter

from app.core.yandex_client import YandexDiskClient


def format_time_delta(delta: timedelta) -> str:
    """
    Форматирует timedelta в читаемый формат.

    Args:
        delta: Объект timedelta

    Returns:
        str: Отформатированная строка времени

    Примеры:
        - "5 дн. 3 ч." — если есть дни
        - "2 ч. 30 мин." — если только часы и минуты
        - "45 мин." — если только минуты
    """
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60

    parts = []
    if days > 0:
        parts.append(f"{days} дн.")
    if hours > 0:
        parts.append(f"{hours} ч.")
    if minutes > 0:
        parts.append(f"{minutes} мин.")

    if not parts:
        return "0 мин."

    return " ".join(parts)


async def create_simple_report(
    yandex_client: YandexDiskClient,
    filename: str,
    projects: List,
) -> str:
    """
    Создаёт Excel-отчёт и загружает его на Яндекс Диск.

    Args:
        yandex_client: Клиент Яндекс Диска
        filename: Имя файла
        projects: Список проектов для отчёта

    Returns:
        str: Публичная ссылка на файл

    Raises:
        HTTPException: При ошибке создания или загрузки отчёта
    """
    upload_data = await yandex_client.create_excel_file(filename)
    upload_url = upload_data["upload_url"]
    file_path = upload_data["file_path"]

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})

    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#D9EAD3',
        'border': 1,
    })

    cell_format = workbook.add_format({
        'border': 1,
    })

    total_format = workbook.add_format({
        'bold': True,
        'border': 1,
        'bg_color': '#FFF2CC',
    })

    worksheet = workbook.add_worksheet("Отчёт")

    worksheet.merge_range('A1:C1', f'Отчёт о проектах от {filename}', header_format)

    headers = ['Название проекта', 'Время сбора', 'Описание']
    for col, header in enumerate(headers):
        worksheet.write(1, col, header, header_format)

    row = 2
    for project in projects:
        if project.close_date and project.create_date:
            delta = project.close_date - project.create_date
            time_str = format_time_delta(delta)
        else:
            time_str = "Не завершён"

        worksheet.write(row, 0, project.name, cell_format)
        worksheet.write(row, 1, time_str, cell_format)
        worksheet.write(row, 2, project.description, cell_format)
        row += 1

    worksheet.write(row, 0, f'Всего проектов: {len(projects)}', total_format)
    worksheet.merge_range(row, 1, row, 2, '', total_format)

    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:C', 50)

    workbook.close()

    output.seek(0)

    await yandex_client.upload_file(upload_url, output.getvalue())

    public_url = await yandex_client.publish_file(file_path)

    return public_url