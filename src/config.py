import os
from dotenv import load_dotenv
from pathlib import Path

# загружаем .env один раз при импорте
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

ELASTIC_HOST = os.getenv("ELASTIC_HOST")
INDEX_NAME = os.getenv("INDEX_NAME")

RABBITMQ_PASS=os.getenv("RABBITMQ_PASS")
RABBITMQ_LOG=os.getenv("RABBITMQ_LOG")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_PORT = os.getenv("MINIO_PORT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_USE_SSL = os.getenv("MINIO_USE_SSL", "false").lower() == "true"
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "info-hub")