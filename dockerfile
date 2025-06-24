# --- Stage 1: Builder ---
FROM python:3.11.9-slim-bookworm as builder

ENV PIP_NO_CACHE_DIR=on \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Installiamo le dipendenze di sistema necessarie per l'esecuzione di OpenCV (cv2)
# libgl1 fornisce il file libGL.so.1 che mancava.
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 && \
    rm -rf /var/lib/apt/lists/*

# Non è più necessario installare git
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install -r requirements.txt


# --- Stage 2: Final ---
FROM python:3.11.9-slim-bookworm

WORKDIR /app

RUN useradd --create-home appuser
USER appuser

# Copiamo le dipendenze E GLI ESEGUIBILI dallo stage "builder"
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin 

# Copiamo il codice della nostra applicazione
COPY --chown=appuser:appuser ./api ./api

# Impostiamo una porta di default. Render la sovrascriverà con la sua.
ENV PORT=8001

# --- RIGA CORRETTA ---
# Usiamo la "shell form" per permettere l'espansione della variabile $PORT
CMD gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app --bind 0.0.0.0:$PORT
