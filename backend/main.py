import os
import hashlib
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from backend.config import settings
from backend.services import rag_service

app = FastAPI(title=settings.PROJECT_NAME)

class ChatRequest(BaseModel):
    """
    Pydantic model representing a chat request payload.
    """
    question: str
    
def get_file_hash(filepath: str) -> str:
    """
    Calculate the SHA-256 hash of a file's content.

    Parameters
    ----------
    filepath : str
        The absolute or relative path to the file.

    Returns
    -------
    str
        The hexadecimal representation of the file's SHA-256 hash.
    """
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)) -> dict:
    """
    Upload a PDF file, check for content duplicates, save it to the local 
    directory, and process it into the vector database.

    Parameters
    ----------
    file : UploadFile, default=File(...)
        The uploaded PDF file object provided via multipart/form-data.

    Returns
    -------
    dict
        A dictionary containing a success message upon successful processing.

    Raises
    ------
    HTTPException
        - 400: If the uploaded file is not a PDF.
        - 409: If a file with identical content or the same name (but different content) already exists.
        - 500: If document processing fails.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_bytes = await file.read()
    incoming_hash = hashlib.sha256(file_bytes).hexdigest()
    for existing_file in os.listdir(settings.UPLOAD_DIR):
        if existing_file.endswith(".pdf"):
            existing_path = os.path.join(settings.UPLOAD_DIR, existing_file)
            if get_file_hash(existing_path) == incoming_hash:
                raise HTTPException(
                    status_code=409, 
                    detail=f"File with identical content already exists as '{existing_file}'."
                )
    
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    
    if os.path.exists(file_path):
        raise HTTPException(
            status_code=409, 
            detail="File with this name already exists but has different content. Rename it first."
        )
    
    with open(file_path, "wb") as buffer:
        buffer.write(file_bytes)
        
    try:
        rag_service.process_pdf(file_path)
        return {"message": f"The file {file.filename} has been processed!"}
    except Exception as e:
        if os.path.exists(file_path): os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files")
async def list_files() -> dict:
    """
    Retrieve a list of all PDF files currently stored in the upload directory.

    Returns
    -------
    dict
        A dictionary containing a list of filenames under the key "files".
    """
    files = [f for f in os.listdir(settings.UPLOAD_DIR) if f.endswith(".pdf")]
    return {"files": files}

@app.delete("/files/{filename}")
async def delete_file(filename: str) -> dict:
    """
    Delete a specific PDF document from both the local filesystem and the vector database.

    Parameters
    ----------
    filename : str
        The name of the PDF file to delete.

    Returns
    -------
    dict
        A dictionary containing a success message upon successful deletion.

    Raises
    ------
    HTTPException
        - 500: If the deletion process fails in the vector database or filesystem.
    """
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    try:
        rag_service.delete_document(file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"message": f"Deleted {filename} from database."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_docs(request: ChatRequest) -> dict:
    """
    Process a user query, retrieve relevant document context, and generate an answer.

    Parameters
    ----------
    request : ChatRequest
        A Pydantic model containing the user's question.

    Returns
    -------
    dict
        A dictionary containing the generated answer under the key "answer".

    Raises
    ------
    HTTPException
        - 500: If the RAG service fails to generate an answer.
    """
    try:
        answer = rag_service.answer_question(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))