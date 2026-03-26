import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME = "RAG API"
    QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
    COLLECTION_NAME = "rag_collection"
    EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL = "gemini-2.5-flash"
    UPLOAD_DIR = "uploads"

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)