
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gdal-bin \
        libgdal-dev \
        libexpat1 \
        g++ \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY alembic.ini ./
COPY alembic/ ./alembic/

RUN python -m pip install --upgrade pip \
    && python -m pip install ".[dev]"

COPY app/ ./app/
COPY tests/ ./tests/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
