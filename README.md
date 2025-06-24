# Memvid API Backend

Questa è l'API backend del progetto Memvid, costruita con [FastAPI](https://fastapi.tiangolo.com/). Funge da interfaccia per interagire con la libreria [Memvid](https://github.com/olow304/memvid), permettendo di creare, gestire e interrogare memorie documentali tramite un modello linguistico (LLM).

Questo backend è progettato per essere usato in combinazione con un'applicazione frontend.

## Funzionalità Principali

* **Gestione Memorie**: Crea memorie da file (`.txt`, `.pdf`) o da chunk di testo. Elenca e cancella le memorie esistenti.
* **Interrogazione Intelligente**: Poni una domanda in linguaggio naturale a una memoria per ricevere una risposta generata da un LLM.
* **Containerizzato con Docker**: Include un `Dockerfile` multi-stage per un deploy di produzione pulito, sicuro e riproducibile.
* **Test Suite**: Include una suite di test con `pytest` per verificare il corretto funzionamento degli endpoint.

## Guida all'Installazione e Configurazione Locale

### 1. Setup dell'Ambiente
```bash
# Clona il repository
git clone <URL_DEL_TUO_REPO_BACKEND>
cd memvid-api

# Crea e attiva un ambiente virtuale
python -m venv .venv
# Su Windows:
.\.venv\Scripts\activate
# Su macOS/Linux:
source .venv/bin/activate

# Installa tutte le dipendenze
pip install -r requirements.txt
```

### 2. Configurazione delle Variabili d'Ambiente
Copia le tue chiavi API in un file `.env` nella cartella principale del progetto. Questo file è ignorato da Git per sicurezza.

**File: `.env`**
```
GOOGLE_API_KEY="LA_TUA_CHIAVE_API_QUI"
CORS_ORIGINS="http://localhost:5173"
```

### 3. Avvio del Server Locale
Avvia il server di sviluppo con Uvicorn.
```bash
uvicorn api.main:app --reload --port 8001
```

## Utilizzo con Docker (Locale)

Per eseguire l'applicazione in un ambiente isolato e identico a quello di produzione, puoi usare Docker.

**Prerequisiti:**
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installato e in esecuzione.

**1. Costruisci l'Immagine Docker**
Esegui questo comando dalla cartella principale del progetto.
```bash
docker build -t memvid-api .
```

**2. Avvia il Container Docker**
Questo comando avvia l'API sulla porta 8001 e collega una cartella locale per salvare le memorie in modo persistente.
```powershell
# In PowerShell (sostituisci la chiave API)
docker run -d -p 8001:8001 --name memvid-api-container -v ${pwd}/memvid_memories_local:/app/memvid_memories -e GOOGLE_API_KEY="LA_TUA_CHIAVE_API_QUI" -e CORS_ORIGINS="http://localhost:5173" -e PORT=8001 memvid-api

# In CMD di Windows, usa %cd% invece di ${pwd}
```
L'API sarà ora accessibile su `http://localhost:8001`.

## Documentazione API

Il modo più semplice per testare gli endpoint è tramite la documentazione interattiva (Swagger UI), disponibile a **[http://localhost:8001/docs](http://localhost:8001/docs)** quando il server (locale o Docker) è in esecuzione.

*(Elenco degli endpoint come prima)*

## Eseguire i Test
Per lanciare la suite di test automatizzati:
```bash
pytest
```

## Deployment in Produzione (Render)
Questo progetto è pronto per il deploy su piattaforme che supportano Docker, come Render.

1.  Collega il tuo repository a un nuovo "Web Service" su Render.
2.  Seleziona **`Docker`** come **Runtime**. Render userà automaticamente il `Dockerfile`.
3.  Nella sezione "Environment" di Render, imposta le variabili d'ambiente `GOOGLE_API_KEY` e `CORS_ORIGINS`.
4.  Aggiungi un "Disk" per lo storage persistente, impostando il "Mount Path" a `/app/memvid_memories`.