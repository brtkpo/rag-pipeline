## RAG System for PDF Documents
Containerized RAG architecture for context-driven question answering over uploaded PDF documents.

---

## Tech Stack

* **Backend:** FastAPI, Python 3.12
* **Frontend:** Streamlit
* **AI & NLP:** LangChain, Google Gemini (`gemini-2.5-flash`), HuggingFace Embeddings (`all-MiniLM-L6-v2`)
* **Vector Store:** Qdrant
* **Infrastructure:** Docker, Docker Compose
---

## Quick Start

1. Clone the repository:
```bash
   git clone https://github.com/brtkpo/rag-pipeline.git
   cd rag-pipeline
```
2. Set up your environment variables:
Create a `.env` file in the root directory and add your Google API key (required for the Gemini model):
`GOOGLE_API_KEY=your_google_api_key_here`

3. Build and start the application:
```bash
   docker-compose up --build
``` 

4. Open your browser and navigate to:
* Frontend: `http://localhost:8501`
* Backend: `http://localhost:8000/docs`
---

## API Endpoints
The backend provides a REST API with the following key endpoints:
- `POST /upload` – Uploads a PDF, checks SHA-256 hash for duplicates, chunks the text, and stores embeddings in Qdrant. 
- `GET /files` – Lists all successfully processed documents.
- `DELETE /files/{filename}` – Removes the document from local storage and deletes associated vectors from Qdrant.
- `POST /chat` – Takes a user query, retrieves context from Qdrant, applies guardrails, and returns the LLM-generated answer.
---
