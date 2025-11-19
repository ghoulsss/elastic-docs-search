import asyncio
import os
import uuid
from minio import Minio, S3Error
from config import (
    MINIO_ENDPOINT,
    MINIO_PORT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_USE_SSL,
)


minio_client = Minio(
    f"{MINIO_ENDPOINT}:{MINIO_PORT}",
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_USE_SSL,
)
DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)


# Синхронная функция скачивания PDF
def download_pdf_sync(bucket: str, path: str) -> bytes:
    object_name = path.lstrip("/")
    # Проверяем, что файл существует
    try:
        minio_client.stat_object(bucket, object_name)
    except S3Error as e:
        if e.code == "NoSuchKey":
            raise FileNotFoundError(f"Файл не найден в MinIO: {bucket}/{object_name}")
        else:
            raise

    response = minio_client.get_object(bucket, object_name)

    try:
        pdf_bytes = response.read()
    finally:
        response.close()
        response.release_conn()

    return pdf_bytes


# --- АСИНХРОННАЯ ОБЁРТКА ---
async def download_pdf_from_minio(bucket: str, path: str) -> bytes:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, download_pdf_sync, bucket, path)


async def download_pdf_from_message(message: dict):
    """
    Получаем PDF по сообщению из брокера, сохраняем в downloads с рандомным именем.
    Возвращаем путь к файлу.
    message = {
        "cardId": 247,
        "file": {
            "bucket": "info-hub",
            "url": "Documents/203/File/dae7cc74-a053-49cb-ab06-4e1c27c7945d.pdf"
        }
    }
    """
    file_info = message.get("file")
    if not file_info:
        raise ValueError("В сообщении нет информации о файле")

    bucket = file_info["bucket"]  # ← было file_info["file"]["bucket"]
    path = file_info["url"]  # ← было file_info["file"]["url"]

    pdf_bytes = await download_pdf_from_minio(bucket, path)

    # генерируем рандомное имя
    random_filename = f"{uuid.uuid4()}.pdf"
    local_path = os.path.join(DOWNLOADS_DIR, random_filename)

    # сохраняем на диск
    with open(local_path, "wb") as f:
        f.write(pdf_bytes)

    print(
        f"PDF скачан из bucket='{bucket}', path='{path}', сохранён в {local_path}, размер = {len(pdf_bytes)} байт"
    )

    return local_path
