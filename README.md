# API per Memvid

Questo repository contiene il codice per un'API web costruita con [FastAPI](https://fastapi.tiangolo.com/) che funge da interfaccia per interagire con la libreria [Memvid](https://github.com/olow304/memvid). L'obiettivo è permettere il caricamento di documenti e l'interrogazione della memoria di Memvid tramite semplici chiamate HTTP.

**Stato del progetto:** Attualmente il progetto è un *boilerplate* funzionante, con gli endpoint dell'API definiti e pronti. La logica di business per l'integrazione con Memvid non è ancora stata implementata.

## Struttura del Progetto

```
.
├── api/
│   ├── main.py         # Entry point dell'applicazione FastAPI
│   ├── models.py       # Modelli di dati Pydantic
│   └── routes.py       # Definizione degli endpoint dell'API
├── .venv/              # Ambiente virtuale di Python (ignorato da Git)
└── requirements.txt    # Dipendenze della libreria Memvid
```

## Setup e Installazione

Per eseguire questo progetto in locale, segui questi passaggi.

**1. Clona il repository**
```bash
git clone <URL_DEL_TUO_REPOSITORY>
cd <NOME_DELLA_CARTELLA>
```

**2. Crea e attiva un ambiente virtuale**
```bash
# Crea l'ambiente
python -m venv .venv

# Attiva l'ambiente (Windows)
.venv\Scripts\activate

# Attiva l'ambiente (macOS/Linux)
source .venv/bin/activate
```

**3. Installa le dipendenze**
Questo progetto richiede sia le librerie di `memvid` che quelle per l'API web.

```bash
# Installa le dipendenze di memvid
pip install -r requirements.txt

# Installa le dipendenze dell'API (FastAPI, Uvicorn, etc.)
pip install "fastapi[all]"
```
> **Nota:** Per una gestione più pulita, potresti voler aggiungere `"fastapi[all]"` al tuo file `requirements.txt`.

## Avviare l'Applicazione

Con l'ambiente virtuale attivo, avvia il server di sviluppo con Uvicorn:

```bash
uvicorn api.main:app --reload
```

Il server sarà in ascolto all'indirizzo `http://127.0.0.1:8000`. L'opzione `--reload` ricaricherà il server automaticamente ad ogni modifica del codice.

## Endpoint dell'API

Una volta avviato il server, puoi accedere alla documentazione interattiva (generata da Swagger UI) per testare gli endpoint.

* **Documentazione Interattiva: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

### Endpoint Disponibili

* `GET /`: Endpoint di benvenuto.
* `POST /api/upload-documents`: Endpoint per caricare uno o più file (logica da implementare).
* `POST /api/add-chunks`: Endpoint per inviare una lista di "chunk" di testo (logica da implementare).
* `POST /api/query`: Endpoint per inviare una query e ricevere una risposta (logica da implementare).

## Come Eseguire il Debug

Questo progetto è pre-configurato per il debug in Visual Studio Code.

1.  Imposta un breakpoint nel codice (es. in `api/routes.py`).
2.  Vai alla vista "Run and Debug" (`Ctrl+Shift+D`).
3.  Seleziona **"Python: Debug FastAPI"** dal menu a tendina e premi F5.
4.  Esegui una richiesta all'endpoint dove hai messo il breakpoint tramite la documentazione per attivare il debugger.
