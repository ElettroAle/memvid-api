# Memvid API

Questa è un'API web funzionale, costruita con [FastAPI](https://fastapi.tiangolo.com/), che funge da interfaccia per interagire con la libreria [Memvid](https://github.com/olow304/memvid). L'API permette di creare "memorie" da documenti o da chunk di testo e di interrogarle successivamente tramite un modello linguistico (LLM).

## Funzionalità Principali

* **Creazione di Memorie da File**: Carica uno o più file (`.txt`, `.pdf`) per creare una nuova memoria `memvid`.
* **Creazione di Memorie da Testo**: Invia una lista di stringhe (chunk) per creare una nuova memoria.
* **Interrogazione Intelligente**: Poni una domanda in linguaggio naturale a una memoria esistente per ricevere una risposta generata da un LLM, basata sul contesto estratto dai documenti.
* **Gestione Organizzata**: Ogni memoria viene salvata in una cartella dedicata per una facile gestione.
* **Test Suite**: Include una suite di unit test con `pytest` per verificare il corretto funzionamento degli endpoint.

## Struttura del Progetto

```
memvid-api/
├── .venv/                  # Ambiente virtuale Python (ignorato da Git)
├── api/                    # Codice sorgente dell'API FastAPI
│   ├── main.py
│   ├── models.py
│   └── routes.py
├── memvid_memories/        # Directory dove vengono salvate le memorie create
├── temp_uploads/           # Cartella per i file caricati temporaneamente
├── tests/                  # Unit test per l'API
│   └── test_api.py
├── .gitignore
├── README.md
└── requirements.txt        # Lista delle dipendenze del progetto
```

## 1. Setup dell'Ambiente e Installazione

Per eseguire questo progetto in locale, segui questi passaggi.

**a. Clona il repository**
```bash
git clone <URL_DEL_TUO_REPOSITORY>
cd memvid-api
```

**b. Crea e attiva un ambiente virtuale**
L'ambiente virtuale isola le dipendenze di questo progetto dal resto del sistema.

```bash
# Crea l'ambiente
python -m venv .venv

# Attiva l'ambiente (Windows)
.\.venv\Scripts\activate

# Attiva l'ambiente (macOS/Linux)
source .venv/bin/activate
```

**c. Installa tutte le dipendenze**
Il file `requirements.txt` è configurato per installare tutto il necessario, inclusa la libreria `memvid` direttamente da GitHub.
```bash
pip install -r requirements.txt
```

## 2. Configurazione di Visual Studio Code

La cartella `.vscode`, che contiene le impostazioni dell'editor, è volutamente inclusa nel file `.gitignore`. Questo perché le configurazioni possono essere specifiche per ogni utente. Di seguito sono riportati i passaggi per configurare VS Code da zero per questo progetto.

**a. Seleziona l'Interprete Python**
Dobbiamo dire a VS Code di usare l'interprete Python del nostro ambiente virtuale.

1.  Apri la "Command Palette" (`Ctrl+Shift+P` o `Cmd+Shift+P` su Mac).
2.  Digita e seleziona **"Python: Select Interpreter"**.
3.  Scegli l'interprete che si trova nel percorso `.\.venv\Scripts\python.exe`. VS Code lo creerà o aggiornerà il file `.vscode/settings.json` per te.

**b. Configura il Debugger (tasto F5)**
Per poter avviare e debuggare l'applicazione premendo F5, è necessario creare un file di configurazione per il debugger.

1.  Crea una cartella `.vscode` nella root del progetto (se non esiste già).
2.  All'interno di `.vscode`, crea un file chiamato `launch.json`.
3.  Incolla il seguente contenuto nel file `launch.json`:

    ```json
    {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Debug FastAPI",
                "type": "debugpy",
                "request": "launch",
                "module": "uvicorn",
                "args": [
                    "api.main:app",
                    "--reload",
                    "--port", 
                    "8001"
                ],
                "jinja": true,
                "justMyCode": true
            }
        ]
    }
    ```

## 3. Configurazione delle Chiavi API (Variabili d'Ambiente)

Per poter interrogare una memoria, l'API utilizza un modello linguistico che richiede una chiave API. Assicurati di impostare la variabile d'ambiente corretta nel tuo terminale prima di avviare il server.

**Esempio (se usi Google Gemini):**
```powershell
# In PowerShell (Windows)
$env:GOOGLE_API_KEY="LA_TUA_CHIAVE_API_QUI"

# In Bash (macOS/Linux)
export GOOGLE_API_KEY="LA_TUA_CHIAVE_API_QUI"
```

## 4. Avvio dell'Applicazione

Con l'ambiente virtuale attivo e le variabili d'ambiente impostate, puoi avviare il server direttamente da VS Code premendo **F5**, oppure manualmente dal terminale:

```bash
uvicorn api.main:app --reload --port 8001
```

## 5. Utilizzo dell'API

### Documentazione Interattiva
Il modo più semplice per testare l'API è tramite la documentazione interattiva (Swagger UI), disponibile all'indirizzo che hai configurato (es. **[http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)**).

*(Gli esempi di `curl` rimangono invariati)*

## 6. Eseguire i Test

Per assicurarti che tutto funzioni correttamente, puoi lanciare la suite di test automatizzati.
```bash
pytest
```