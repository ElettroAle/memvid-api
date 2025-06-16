from fastapi import APIRouter, UploadFile, File
from typing import List
from .models import AddChunksRequest, QueryRequest, ApiResponse

import shutil
import os

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}

@router.post("/upload-multiple/")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    filenames = []
    for file in files:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        filenames.append(file.filename)
    return {"filenames": filenames}

@router.post("/upload-documents", response_model=ApiResponse, tags=["Memory"])
async def upload_documents(
    files: List[UploadFile] = File(..., description="Uno o più documenti da caricare.")
):
    """
    Endpoint per caricare uno o più documenti.
    (Logica di processing non ancora implementata)
    """
    filenames = [file.filename for file in files]
    print(f"Ricevuti {len(filenames)} file: {filenames}")
    
    return ApiResponse(
        message="Documenti ricevuti con successo.",
        data={"files_uploaded": filenames}
    )

@router.post("/add-chunks", response_model=ApiResponse, tags=["Memory"])
async def add_chunks(request: AddChunksRequest):
    """
    Endpoint per aggiungere chunk di testo alla memoria.
    (Logica di processing non ancora implementata)
    """
    num_chunks = len(request.chunks)
    print(f"Ricevuti {num_chunks} chunk di testo.")
    
    return ApiResponse(
        message=f"{num_chunks} chunk di testo ricevuti con successo.",
        data={"chunk_count": num_chunks}
    )

@router.post("/query", response_model=ApiResponse, tags=["Query"])
async def query_memory(request: QueryRequest):
    """
    Endpoint per interrogare la memoria.
    (Logica di interrogazione non ancora implementata)
    """
    print(f"Ricevuta query: '{request.query}'")
    
    # Risposta simulata
    return ApiResponse(
        message="Query ricevuta.",
        data={
            "your_query": request.query,
            "response": "Questa è una risposta simulata. La logica di ricerca non è ancora collegata."
        }
    )