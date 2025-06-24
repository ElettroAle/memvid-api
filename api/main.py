import os
from fastapi import FastAPI
from .routes import router as api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Memvid API Boilerplate",
    description="Un'API web per caricare documenti e interrogare una memoria. Logica di business non ancora implementata.",
    version="0.0.1",
)

# Leggi la variabile d'ambiente "CORS_ORIGINS".
# Se non la trova, usa un valore di default (l'URL di sviluppo locale).
# La stringa può contenere più URL separati da virgola.
origins_str = os.getenv("CORS_ORIGINS", "http://localhost:5173")

# 3. Dividi la stringa in una lista di URL, togliendo eventuali spazi
origins = [origin.strip() for origin in origins_str.split(',')]

# 4. Aggiungi il middleware usando la lista di origini dinamica
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Applica le regole CORS a tutti gli endpoint.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permette tutti i metodi (GET, POST, DELETE, etc.)
    allow_headers=["*"], # Permette tutti gli header
)

# Include tutte le route definite nel file routes.py sotto il prefisso /api
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
async def read_root():
    """Endpoint di benvenuto."""
    return {"message": "Benvenuto nell'API. Vai su /docs per la documentazione."}