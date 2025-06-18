from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

# --- MODELLI PER LE RICHIESTE ---

class CreateMemoryFromChunksRequest(BaseModel):
    """Richiesta per creare una memoria da una lista di chunk di testo."""
    memory_name: str = Field(..., description="Nome univoco per la memoria che verrà creata.")
    chunks: List[str] = Field(..., description="Lista di testi da aggiungere.", min_items=1)

class QueryRequest(BaseModel):
    """Richiesta per interrogare una memoria."""
    memory_name: str = Field(..., description="Il nome della memoria da interrogare.")
    query: str = Field(..., description="La domanda da sottoporre.")
    top_k: int = Field(5, description="Numero di risultati di contesto da recuperare.")

# --- MODELLI PER LE RISPOSTE ---

class MemoryCreationResponse(BaseModel):
    """Risposta generica dopo la creazione di una memoria."""
    message: str
    memory_name: str
    video_path: str
    index_path: str
    stats: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    """Risposta dettagliata a una query."""
    response: str
    context: List[str]