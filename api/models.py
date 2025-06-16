from pydantic import BaseModel, Field
from typing import List

class AddChunksRequest(BaseModel):
    """Richiesta per aggiungere una lista di chunk di testo."""
    chunks: List[str] = Field(..., description="Lista di testi da aggiungere.", min_items=1)

class QueryRequest(BaseModel):
    """Richiesta per interrogare la memoria."""
    query: str = Field(..., description="La domanda da sottoporre.")

class ApiResponse(BaseModel):
    """Risposta generica dell'API."""
    message: str
    data: dict = {}