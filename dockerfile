# --- Stage 1: Builder ---
FROM python:3.11.9-slim-bookworm as builder

ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.8.2 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Aggiorniamo i pacchetti E INSTALLIAMO GIT
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools
RUN pip install --no-cache-dir -r requirements.txt


# --- Stage 2: Final ---
FROM python:3.11.9-slim-bookworm

WORKDIR /app

RUN useradd --create-home appuser
USER appuser

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --chown=appuser:appuser ./api ./api

ENV PORT 8000

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "api.main:app", "--bind", "0.0.0.0:$PORT"]