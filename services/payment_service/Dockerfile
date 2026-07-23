# ---- Base ----
FROM python:3.12-slim-bookworm AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy service code
COPY services/payment_service .

# Copy shared folder
COPY shared ./shared

# Copy requirements
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

RUN useradd -m django && chown -R django:django /app
USER django

# ---- Production ----
FROM base AS production
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

# ---- Development ----
FROM base AS development
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
