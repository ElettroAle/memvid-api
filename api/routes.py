import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body
from typing import List

# Importiamo le classi principali di Memvid
from memvid import MemvidEncoder, MemvidChat
from memvid.config import get_codec_parameters

# Importiamo i nostri modelli Pydantic aggiornati
from .models import CreateMemoryFromChunksRequest, QueryRequest, MemoryCreationResponse, QueryResponse, ListMemoriesResponse


router = APIRouter()

# Definiamo delle directory di base per i file temporanei e le memorie permanenti
UPLOAD_DIR = "temp_uploads"
MEMORY_DIR = "memvid_memories"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MEMORY_DIR, exist_ok=True)

@router.post("/create-from-files", response_model=MemoryCreationResponse, tags=["Memory Creation"])
async def create_memory_from_files(
    memory_name: str = Form(..., description="Nome univoco per la memoria da creare."),
    files: List[UploadFile] = File(..., description="Uno o più documenti (PDF, TXT) da cui creare la memoria.")
):
    """
    Crea una memoria Memvid da una lista di file caricati.
    """
    # Creiamo una cartella specifica per questa memoria
    memory_path = os.path.join(MEMORY_DIR, memory_name)
    if os.path.exists(memory_path):
        raise HTTPException(status_code=409, detail=f"Una memoria con il nome '{memory_name}' esiste già.")
    os.makedirs(memory_path)

    encoder = MemvidEncoder()

    # Otteniamo il codec e l'estensione che l'encoder userà di default
    actual_codec = encoder.config.get("codec")
    codec_params = get_codec_parameters(actual_codec)
    video_ext = codec_params.get("video_file_type", "mp4")

    temp_file_paths = []

    try:
        # Salviamo i file temporaneamente
        for file in files:
            temp_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            temp_file_paths.append(temp_path)

            # Aggiungiamo il contenuto all'encoder in base al tipo di file
            if file.filename.lower().endswith(".pdf"):
                encoder.add_pdf(temp_path)
            elif file.filename.lower().endswith(".txt"):
                with open(temp_path, "r", encoding="utf-8") as f:
                    encoder.add_text(f.read())
            else:
                # Puoi aggiungere qui il supporto per altri tipi di file
                print(f"File non supportato: {file.filename}, verrà ignorato.")

        if not encoder.chunks:
            raise HTTPException(status_code=400, detail="Nessun contenuto valido trovato nei file forniti.")

        # Costruiamo la memoria video e l'indice
        video_output_path = os.path.join(memory_path, f"memory.{video_ext}")
        index_output_path = os.path.join(memory_path, "index.json")
        stats = encoder.build_video(video_output_path, index_output_path)

        return MemoryCreationResponse(
            message="Memoria creata con successo dai file.",
            memory_name=memory_name,
            video_path=video_output_path,
            index_path=index_output_path,
            stats=stats
        )

    except Exception as e:
        # In caso di errore, rimuoviamo la cartella della memoria creata parzialmente
        if os.path.exists(memory_path):
            shutil.rmtree(memory_path)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Puliamo i file temporanei
        for path in temp_file_paths:
            os.remove(path)


@router.post("/create-from-chunks", response_model=MemoryCreationResponse, tags=["Memory Creation"])
async def create_memory_from_chunks(request: CreateMemoryFromChunksRequest):
    """
    Crea una memoria Memvid direttamente da una lista di chunk di testo.
    """
    memory_path = os.path.join(MEMORY_DIR, request.memory_name)
    if os.path.exists(memory_path):
        raise HTTPException(status_code=409, detail=f"Una memoria con il nome '{request.memory_name}' esiste già.")
    os.makedirs(memory_path)
    
    try:
        encoder = MemvidEncoder()
        encoder.add_chunks(request.chunks)

        video_output_path = os.path.join(memory_path, "memory.mp4")
        index_output_path = os.path.join(memory_path, "index.json")
        stats = encoder.build_video(video_output_path, index_output_path)

        return MemoryCreationResponse(
            message="Memoria creata con successo dai chunk.",
            memory_name=request.memory_name,
            video_path=video_output_path,
            index_path=index_output_path,
            stats=stats
        )
    except Exception as e:
        if os.path.exists(memory_path):
            shutil.rmtree(memory_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_memory(request: QueryRequest):
    """
    Interroga una memoria esistente usando una query di testo.
    """
    memory_path = os.path.join(MEMORY_DIR, request.memory_name)
    video_file = os.path.join(memory_path, "memory.mp4")
    index_file = os.path.join(memory_path, "index.json")

    if not os.path.exists(video_file) or not os.path.exists(index_file):
        raise HTTPException(status_code=404, detail=f"Memoria '{request.memory_name}' non trovata.")

    try:
        # Assicurati che le chiavi API per il provider LLM siano impostate come variabili d'ambiente
        # Esempio: GOOGLE_API_KEY, OPENAI_API_KEY
        chat = MemvidChat(video_file=video_file, index_file=index_file)
        
        # Recuperiamo sia la risposta diretta che il contesto usato
        response_text = chat.chat(request.query)
        context = chat.retriever.search(request.query, top_k=request.top_k)

        return QueryResponse(
            response=response_text,
            context=context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/memories/", response_model=ListMemoriesResponse, tags=["Memory Management"])
async def list_memories():
    """
    Restituisce una lista dei nomi di tutte le memorie create.
    """
    if not os.path.exists(MEMORY_DIR):
        # Se la directory base non esiste, non ci sono memorie
        return ListMemoriesResponse(memories=[])
    
    try:
        # Elenchiamo solo le directory all'interno della cartella delle memorie
        memory_names = [name for name in os.listdir(MEMORY_DIR) if os.path.isdir(os.path.join(MEMORY_DIR, name))]
        return ListMemoriesResponse(memories=memory_names)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante la lettura delle memorie: {e}")    

@router.delete("/memory/{memory_name}", tags=["Memory Management"])
async def delete_memory(memory_name: str):
    """
    Cancella permanentemente una memoria esistente e tutti i suoi file.
    """
    memory_path = os.path.join(MEMORY_DIR, memory_name)

    # Controlliamo se la memoria esiste prima di provare a cancellarla
    if not os.path.exists(memory_path):
        raise HTTPException(status_code=404, detail=f"Memoria '{memory_name}' non trovata.")

    try:
        # shutil.rmtree cancella una cartella e tutto il suo contenuto
        shutil.rmtree(memory_path)
        return {"message": f"Memoria '{memory_name}' cancellata con successo."}
    except Exception as e:
        # Gestiamo eventuali errori durante la cancellazione
        raise HTTPException(status_code=500, detail=f"Errore durante la cancellazione della memoria: {e}")