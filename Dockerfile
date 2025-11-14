FROM python:3.12-bullseye

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    TZ="Europe/Moscow"

RUN pip install --upgrade pip --no-cache-dir && \
    pip install poetry --no-cache-dir

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-cache --no-ansi --only main

COPY . .
