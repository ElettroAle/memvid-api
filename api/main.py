from fastapi import FastAPI
from .routes import router as api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Memvid API Boilerplate",
    description="Un'API web per caricare documenti e interrogare una memoria. Logica di business non ancora implementata.",
    version="0.0.1",
)

origins = [
    "http://localhost:5173",  # L'indirizzo del tuo server di sviluppo React/Vite
    # In futuro qui aggiungerai l'URL di produzione
]

# Applica le regole CORS a tutti gli endpoint.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permette tutti i metodi (GET, POST, DELETE, etc.)
    allow_headers=["*"], # Permette tutti gli header
)

# Include tutte le route definite nel file routes.py sotto il prefisso /api
app.include_router(api_router, prefix="/api")

@app.get("/", tags=["Root"])
async def read_root():
    """Endpoint di benvenuto."""
    return {"message": "Benvenuto nell'API. Vai su /docs per la documentazione."}