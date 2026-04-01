import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    Configuration settings for the RAG API application.

    This class loads environment variables and sets default values for 
    various components of the system, including the vector database, 
    embedding models, and local storage.

    Attributes
    ----------
    PROJECT_NAME : str
        The name of the FastAPI project/application.
    QDRANT_URL : str
        The connection URL for the Qdrant vector database instance. Defaults
        to 'http://qdrant:6333' if the environment variable is not set.
    COLLECTION_NAME : str
        The base name of the Qdrant collection used for storing document embeddings.
    EMBEDDINGS_MODEL : str
        The HuggingFace model identifier used for generating text embeddings.
    LLM_MODEL : str
        The identifier for the Large Language Model used for text generation.
    UPLOAD_DIR : str
        The local directory path where uploaded PDF files are stored.
    """
    PROJECT_NAME = "RAG API"
    QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
    COLLECTION_NAME = "rag_collection"
    EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL = "gemini-2.5-flash"
    UPLOAD_DIR = "uploads"

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)