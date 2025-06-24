# Memvid API Backend

Questa è l'API backend del progetto Memvid, costruita con [FastAPI](https://fastapi.tiangolo.com/). Funge da interfaccia per interagire con la libreria [Memvid](https://github.com/olow304/memvid), permettendo di creare, gestire e interrogare memorie documentali tramite un modello linguistico (LLM).

Questo backend è progettato per essere usato in combinazione con un'applicazione frontend (es. [memvid-fe](https://github.com/ElettroAle/memvid-fe)).

## Funzionalità Principali

* **Gestione Memorie**: Crea memorie da file (`.txt`, `.pdf`) o da chunk di testo. Elenca e cancella le memorie esistenti.
* **Interrogazione Intelligente**: Poni una domanda in linguaggio naturale a una memoria per ricevere una risposta generata da un LLM.
* **Architettura Pronta per la Produzione**: Include una configurazione basata su variabili d'ambiente e un `Dockerfile` per un deploy semplice e robusto.
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
L'applicazione caricherà automaticamente queste variabili all'avvio.

### 3. Avvio del Server Locale
Avvia il server di sviluppo con Uvicorn. Grazie a `--reload`, si riavvierà automaticamente ad ogni modifica del codice.
```bash
uvicorn api.main:app --reload --port 8001
```

## Documentazione API

L'API espone i seguenti endpoint. Il modo più semplice per testarli è tramite la documentazione interattiva disponibile a **[http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)**.

* `GET /api/memories/`
    * **Descrizione**: Restituisce una lista dei nomi di tutte le memorie create.
    * **Risposta**: `{ "memories": ["memoria1", "memoria2"] }`

* `POST /api/create-from-files`
    * **Descrizione**: Crea una nuova memoria da uno o più file.
    * **Input**: `multipart/form-data` con un campo `memory_name` (stringa) e un campo `files` (uno o più file).

* `POST /api/create-from-chunks`
    * **Descrizione**: Crea una nuova memoria da una lista di stringhe di testo.
    * **Input**: JSON con `memory_name` (stringa) e `chunks` (lista di stringhe).

* `POST /api/query`
    * **Descrizione**: Interroga una memoria esistente.
    * **Input**: JSON con `memory_name` (stringa) e `query` (stringa).

* `DELETE /api/memory/{memory_name}`
    * **Descrizione**: Cancella permanentemente una memoria esistente.
    * **Input**: Il `memory_name` viene passato come parte dell'URL.

## Eseguire i Test
Per lanciare la suite di test automatizzati:
```bash
pytest
```

## Deployment in Produzione (Render)
Questo progetto include un `Dockerfile` per un facile deploy su piattaforme come Render.

1.  Collega il tuo repository a un nuovo "Web Service" su Render.
2.  Render dovrebbe rilevare e usare automaticamente il `Dockerfile`.
3.  Nella sezione "Environment" di Render, imposta le variabili d'ambiente necessarie:
    * `GOOGLE_API_KEY`: La tua chiave API.
    * `CORS_ORIGINS`: L'URL del tuo frontend deployato (es. `https://il-tuo-frontend.vercel.app`).
    * `PORT`: Render imposta questa variabile automaticamente, il nostro `Dockerfile` la userà.
4.  Aggiungi un "Disk" per lo storage persistente, impostando il "Mount Path" a `/app/memvid_memories`.