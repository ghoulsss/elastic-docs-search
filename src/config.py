import os
from dotenv import load_dotenv
from pathlib import Path

# загружаем .env один раз при импорте
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

ELASTIC_HOST = os.getenv("ELASTIC_HOST")
INDEX_NAME = os.getenv("INDEX_NAME")
