from fastapi import FastAPI
from .routes import router as api_router

app = FastAPI(
    title="Memvid API Boilerplate",
    description="Un'API web per caricare documenti e interrogare una memoria. Logica di business non ancora implementata.",
    version="0.0.1",
)

# Include tutte le route definite nel file routes.py sotto il prefisso /api
app.include_router(api_router, prefix="/api")

@app.get("/", tags=["Root"])
async def read_root():
    """Endpoint di benvenuto."""
    return {"message": "Benvenuto nell'API. Vai su /docs per la documentazione."}