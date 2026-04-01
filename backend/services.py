from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, Filter, FieldCondition, MatchValue
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from backend.config import settings

class RAGService:
    """
    Service for handling Retrieval-Augmented Generation operations.

    This class manages the Qdrant vector database connection, document 
    embedding, text splitting, and the LLM interaction for answering questions.
    """
    
    def __init__(self) -> None:
        """
        Initialize the RAG service, vector store, embeddings, and LLM.

        Returns
        -------
        None
        """
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self._init_collection()
        
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDINGS_MODEL)
        self.vector_store = QdrantVectorStore(
            client=self.client, 
            collection_name=settings.COLLECTION_NAME, 
            embedding=self.embeddings
        )
        self.llm = ChatGoogleGenerativeAI(model=settings.LLM_MODEL)

    def _init_collection(self):
        """
        Initialize the Qdrant collection if it does not already exist.

        Returns
        -------
        None
        """
        if not self.client.collection_exists(settings.COLLECTION_NAME):
            self.client.create_collection(
                collection_name=settings.COLLECTION_NAME,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )

    def process_pdf(self, file_path: str):
        """
        Load a PDF document, split it into chunks, and add it to the vector store.

        Parameters
        ----------
        file_path : str
            The absolute or relative path to the PDF file to be processed.

        Returns
        -------
        None
        """
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        split_docs = splitter.split_documents(documents)
        self.vector_store.add_documents(split_docs)

    def delete_document(self, file_path: str):
        """
        Delete all vector embeddings associated with a specific document from the database.

        Parameters
        ----------
        file_path : str
            The path of the file whose associated vectors should be removed.

        Returns
        -------
        None
        """
        self.client.delete(
            collection_name=settings.COLLECTION_NAME,
            points_selector=Filter(
                must=[FieldCondition(key="metadata.source", match=MatchValue(value=file_path))]
            )
        )

    def answer_question(self, question: str) -> str:
        """
        Retrieve relevant document chunks and generate an answer using the LLM.

        Parameters
        ----------
        question : str
            The user's question to be answered based on the document context.

        Returns
        -------
        str
            The generated answer from the LLM, or a fallback statement if the answer
            is not found in the context.
        """
        retriever = self.vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
        prompt = ChatPromptTemplate.from_template("""
        Answer using the provided context. If you don't know the answer, just say that you don't know.
        Context: {context}
        Question: {question}
        """)
        
        rag_chain = (
            {"context": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)), "question": lambda x: x}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        return rag_chain.invoke(question)

rag_service = RAGService()