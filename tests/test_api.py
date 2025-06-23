import os
import shutil
import pytest
from fastapi.testclient import TestClient

# Importiamo l'app FastAPI dal nostro file main
# Assumendo che il tuo progetto sia strutturato in modo che questo import funzioni
# Potrebbe essere necessario aggiungere un __init__.py vuoto nelle cartelle
from api.main import app 

# Definiamo le costanti usate anche nel codice delle routes
MEMORY_DIR = "memvid_memories"

# Creiamo un client di test che useremo in tutte le nostre funzioni di test
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown_test_environment():
    """
    Questa 'fixture' viene eseguita automaticamente prima e dopo ogni test.
    Assicura che partiamo sempre da una situazione pulita.
    """
    # Codice eseguito PRIMA di ogni test
    if os.path.exists(MEMORY_DIR):
        shutil.rmtree(MEMORY_DIR)
    os.makedirs(MEMORY_DIR)
    
    yield  # Qui è dove il test viene eseguito

    # Codice eseguito DOPO ogni test
    if os.path.exists(MEMORY_DIR):
        shutil.rmtree(MEMORY_DIR)


# --- TEST LIST ---

def test_create_memory_from_chunks_success():
    """
    Test 1: Verifica che la creazione di una memoria da chunk di testo funzioni.
    """
    # Arrange: Prepariamo i dati per la richiesta
    test_data = {
        "memory_name": "test_from_chunks",
        "chunks": ["questo è il primo chunk", "questo è il secondo"]
    }

    # Act: Eseguiamo la chiamata all'API
    response = client.post("/api/create-from-chunks", json=test_data)

    # Assert: Verifichiamo i risultati
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["message"] == "Memoria creata con successo dai chunk."
    assert response_json["memory_name"] == "test_from_chunks"
    # Verifichiamo che i file siano stati creati fisicamente
    assert os.path.exists(response_json["video_path"])
    assert os.path.exists(response_json["index_path"])

def test_create_memory_from_files_success():
    """
    Test 2: Verifica che la creazione di una memoria da un file di testo funzioni.
    """
    # Arrange: Creiamo un file di testo fittizio per l'upload
    test_filename = "test_file.txt"
    with open(test_filename, "w", encoding="utf-8") as f:
        f.write("Questo è un file di test.")
    

    memory_name = "test_from_files"
    # Act: Eseguiamo la chiamata all'API inviando il file
    with open(test_filename, "rb") as f:
        response = client.post(
            "/api/create-from-files",
            data={"memory_name": memory_name},
            files={"files": (test_filename, f, "text/plain")}
        )

    # Assert: Verifichiamo i risultati
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["message"] == "Memoria creata con successo dai file."
    assert os.path.exists(os.path.join(MEMORY_DIR, memory_name))

    # Cleanup: Rimuoviamo il file fittizio
    os.remove(test_filename)

def test_create_memory_conflict():
    """
    Test 3: Verifica che l'API restituisca un errore se si cerca di creare una memoria con un nome già esistente.
    """
    # Arrange: Creiamo una prima memoria
    client.post("/api/create-from-chunks", json={"memory_name": "test_conflict", "chunks": ["test"]})

    # Act: Tentiamo di creare una seconda memoria con lo stesso nome
    response = client.post("/api/create-from-chunks", json={"memory_name": "test_conflict", "chunks": ["test 2"]})

    # Assert: Verifichiamo di ricevere un errore 409 Conflict
    assert response.status_code == 409
    assert "esiste già" in response.json()["detail"]

def test_query_memory_not_found():
    """
    Test 4: Verifica che l'API restituisca Not Found se si interroga una memoria inesistente.
    """
    # Act: Chiamiamo l'endpoint di query con un nome di memoria fittizio
    response = client.post("/api/query", json={"memory_name": "memoria_inesistente", "query": "domanda?"})

    # Assert: Verifichiamo di ricevere un errore 404 Not Found
    assert response.status_code == 404

def test_query_memory_success_with_mock(mocker):
    """
    Test 5: Verifica che l'interrogazione di una memoria funzioni.
    IMPORTANTE: Usiamo un 'mock' per simulare la risposta dell'LLM, 
    così il test non dipende da una chiave API o da una connessione a internet.
    """
    # Arrange:
    # 1. Creiamo una memoria su cui fare la query
    memory_name = "test_query"
    client.post("/api/create-from-chunks", json={"memory_name": memory_name, "chunks": ["il cielo è blu"]})
    
    # 2. Mocking: Diciamo a pytest di "intercettare" la creazione di MemvidChat
    # e di sostituire i suoi metodi con delle risposte predefinite.
    mock_chat_response = "Risposta simulata dall'LLM"
    mock_context_response = ["contesto simulato 1"]
    
    mock_chat = mocker.patch('api.routes.MemvidChat')
    # Configuriamo l'istanza mockata per restituire i nostri valori predefiniti
    mock_chat.return_value.chat.return_value = mock_chat_response
    mock_chat.return_value.retriever.search.return_value = mock_context_response

    # Act: Eseguiamo la query
    response = client.post("/api/query", json={"memory_name": memory_name, "query": "di che colore è il cielo?"})

    # Assert: Verifichiamo che la risposta sia corretta
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["response"] == mock_chat_response
    assert response_json["context"] == mock_context_response


def test_delete_memory_success():
    """
    Test 6: Verifica che la cancellazione di una memoria funzioni correttamente.
    """
    # Arrange:
    # 1. Creiamo una memoria da cancellare
    memory_name = "memory_to_delete"
    create_response = client.post("/api/create-from-chunks", json={"memory_name": memory_name, "chunks": ["test delete"]})
    assert create_response.status_code == 200
    
    # 2. Verifichiamo che la cartella della memoria esista davvero
    memory_path = os.path.join(MEMORY_DIR, memory_name)
    assert os.path.exists(memory_path)

    # Act: Eseguiamo la chiamata all'API di cancellazione
    delete_response = client.delete(f"/api/memory/{memory_name}")

    # Assert:
    # 1. Verifichiamo che la risposta sia positiva
    assert delete_response.status_code == 200
    assert "cancellata con successo" in delete_response.json()["message"]
    
    # 2. Verifichiamo che la cartella della memoria sia stata effettivamente cancellata
    assert not os.path.exists(memory_path)

# Inserisci questo test in tests/test_api.py

def test_list_memories():
    """
    Test 8: Verifica che l'API restituisca correttamente la lista delle memorie esistenti.
    """
    # Arrange: Creiamo due memorie per il test
    client.post("/api/create-from-chunks", json={"memory_name": "memoria_uno", "chunks": ["a"]})
    client.post("/api/create-from-chunks", json={"memory_name": "memoria_due", "chunks": ["b"]})

    # Act: Chiamiamo l'endpoint per listare le memorie
    response = client.get("/api/memories/")

    # Assert: Verifichiamo il risultato
    assert response.status_code == 200
    response_data = response.json()
    
    # Usiamo set() per confrontare le liste senza preoccuparci dell'ordine
    assert "memories" in response_data
    assert set(response_data["memories"]) == {"memoria_uno", "memoria_due"}

def test_list_memories_empty():
    """
    Test 9: Verifica che l'API restituisca una lista vuota se non ci sono memorie.
    """
    # Act: Chiamiamo l'endpoint senza aver creato nessuna memoria
    response = client.get("/api/memories/")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {"memories": []}

def test_delete_memory_not_found():
    """
    Test 7: Verifica che l'API restituisca Not Found se si cerca di cancellare una memoria inesistente.
    """
    # Act: Chiamiamo l'endpoint di cancellazione con un nome fittizio
    response = client.delete("/api/memory/memoria_inesistente")

    # Assert: Verifichiamo di ricevere un errore 404 Not Found
    assert response.status_code == 404