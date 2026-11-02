
FROM python:3.12-slim

# ==========================================
# Python Runtime Configuration
# ==========================================

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# ==========================================
# Application Directory
# ==========================================

WORKDIR /app

# ==========================================
# Install Python Dependencies
# ==========================================

COPY pyproject.toml .

RUN python -m pip install --upgrade pip \
    && python -m pip install .

# ==========================================
# Copy Application Source
# ==========================================

COPY app/ ./app/

# ==========================================
# Expose API Port
# ==========================================

EXPOSE 8000

# ==========================================
# Start FastAPI
# ==========================================

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
