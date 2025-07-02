import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List

# Import delle classi e funzioni necessarie da memvid
from memvid import MemvidEncoder, MemvidChat
from memvid.config import get_codec_parameters

from .models import CreateMemoryFromChunksRequest, QueryRequest, MemoryCreationResponse, QueryResponse, ListMemoriesResponse

router = APIRouter()

# --- CONFIGURAZIONE CENTRALIZZATA ---
UPLOAD_DIR = os.getenv("MEMVID_UPLOAD_DIR", "temp_uploads")
MEMORY_DIR = os.getenv("MEMVID_MEMORY_DIR", "memvid_memories")
LIGHTWEIGHT_MODEL = 'all-MiniLM-L6-v2'
# ------------------------------------

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MEMORY_DIR, exist_ok=True)


@router.post("/create-from-files", response_model=MemoryCreationResponse, tags=["Memory Creation"])
async def create_memory_from_files(
    memory_name: str = Form(..., description="Nome univoco per la memoria da creare."),
    files: List[UploadFile] = File(..., description="Uno o più documenti (PDF, TXT) da cui creare la memoria.")
):
    memory_path = os.path.join(MEMORY_DIR, memory_name)
    if os.path.exists(memory_path):
        raise HTTPException(status_code=409, detail=f"Una memoria con il nome '{memory_name}' esiste già.")
    os.makedirs(memory_path)

    # --- CORREZIONE FONDAMENTALE ---
    # Usiamo il parametro corretto "config_overrides" per passare la configurazione
    encoder = MemvidEncoder(config_overrides={'embedding_model': LIGHTWEIGHT_MODEL})
    
    # Otteniamo l'estensione dinamicamente dal codec che l'encoder userà
    actual_codec = encoder.config.get("codec", "h265")
    video_ext = get_codec_parameters(actual_codec).get("video_file_type", "mkv")

    temp_file_paths = []
    try:
        for file in files:
            temp_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            temp_file_paths.append(temp_path)

            if file.filename.lower().endswith(".pdf"):
                encoder.add_pdf(temp_path)
            elif file.filename.lower().endswith(".txt"):
                with open(temp_path, "r", encoding="utf-8", errors='ignore') as f:
                    encoder.add_text(f.read())
            else:
                print(f"File non supportato: {file.filename}, verrà ignorato.")

        if not encoder.chunks:
            raise HTTPException(status_code=400, detail="Nessun contenuto valido trovato nei file forniti.")

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
        if os.path.exists(memory_path):
            shutil.rmtree(memory_path)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        for path in temp_file_paths:
            if os.path.exists(path):
                os.remove(path)


@router.post("/create-from-chunks", response_model=MemoryCreationResponse, tags=["Memory Creation"])
async def create_memory_from_chunks(request: CreateMemoryFromChunksRequest):
    memory_path = os.path.join(MEMORY_DIR, request.memory_name)
    if os.path.exists(memory_path):
        raise HTTPException(status_code=409, detail=f"Una memoria con il nome '{request.memory_name}' esiste già.")
    os.makedirs(memory_path)
    
    try:
        # --- CORREZIONE FONDAMENTALE ---
        # Usiamo anche qui il parametro corretto "config_overrides"
        encoder = MemvidEncoder(config_overrides={'embedding_model': LIGHTWEIGHT_MODEL})
        
        # Rendiamo dinamica l'estensione anche qui per coerenza
        actual_codec = encoder.config.get("codec", "h265")
        video_ext = get_codec_parameters(actual_codec).get("video_file_type", "mkv")

        encoder.add_chunks(request.chunks)

        video_output_path = os.path.join(memory_path, f"memory.{video_ext}")
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
    memory_path = os.path.join(MEMORY_DIR, request.memory_name)
    index_file = os.path.join(memory_path, "index.json")

    video_file = None
    if os.path.exists(memory_path):
        try:
            video_filename = next(f for f in os.listdir(memory_path) if f.startswith("memory."))
            video_file = os.path.join(memory_path, video_filename)
        except StopIteration:
            video_file = None

    if not video_file or not os.path.exists(video_file) or not os.path.exists(index_file):
        raise HTTPException(status_code=404, detail=f"Memoria '{request.memory_name}' non trovata o incompleta.")

    try:
        chat = MemvidChat(video_file=video_file, index_file=index_file)
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
    if not os.path.exists(MEMORY_DIR):
        return ListMemoriesResponse(memories=[])
    try:
        memory_names = [name for name in os.listdir(MEMORY_DIR) if os.path.isdir(os.path.join(MEMORY_DIR, name))]
        return ListMemoriesResponse(memories=memory_names)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante la lettura delle memorie: {e}")


@router.delete("/memory/{memory_name}", tags=["Memory Management"])
async def delete_memory(memory_name: str):
    memory_path = os.path.join(MEMORY_DIR, memory_name)
    if not os.path.exists(memory_path):
        raise HTTPException(status_code=404, detail=f"Memoria '{memory_name}' non trovata.")
    try:
        shutil.rmtree(memory_path)
        return {"message": f"Memoria '{memory_name}' cancellata con successo."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante la cancellazione della memoria: {e}")