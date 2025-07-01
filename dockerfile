# --- Stage 1: Builder ---
FROM python:3.11.9-slim-bookworm as builder

ENV PIP_NO_CACHE_DIR=on \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONUNBUFFERED=1

WORKDIR /app

# --- RIGA MODIFICATA ---
# Aggiorniamo i pacchetti E INSTALLIAMO LE DIPENDENZE DI SISTEMA PER OPENCV
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install -r requirements.txt


# --- Stage 2: Final ---
FROM python:3.11.9-slim-bookworm

WORKDIR /app

RUN useradd --create-home appuser
RUN mkdir -p /app/temp_uploads && chown appuser:appuser /app/temp_uploads
RUN mkdir -p /app/memvid_memories && chown appuser:appuser /app/memvid_memories
USER appuser

# Copiamo le dipendenze E GLI ESEGUIBILI dallo stage "builder"
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin 

# --- RIGA AGGIUNTA ---
# Copiamo anche le librerie di sistema che abbiamo installato
COPY --from=builder /usr/lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu

# Copiamo il codice della nostra applicazione
COPY --chown=appuser:appuser ./api ./api

# Installiamo le dipendenze anche nello stage finale per sicurezza
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=8000
ENV MEMVID_UPLOAD_DIR=/app/temp_uploads
ENV MEMVID_MEMORY_DIR=/app/memvid_memories

# Esponiamo la porta su cui l'applicazione ascolterà
EXPOSE $PORT

# Usiamo la "shell form" per permettere l'espansione della variabile $PORT
CMD uvicorn api.main:app --host 0.0.0.0 --port $PORT