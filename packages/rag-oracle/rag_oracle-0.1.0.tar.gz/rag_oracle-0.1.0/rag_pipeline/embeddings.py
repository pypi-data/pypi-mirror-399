"""
Step 1.3 - Embeddings and Vector Store
Create embeddings and store chunks in a vector database.
"""

import os
from typing import List, Optional
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    # Fallback for older versions
    from langchain_community.embeddings import HuggingFaceEmbeddings


class EmbeddingStore:
    """Create embeddings and manage vector store."""
    
    def __init__(
        self,
        embedding_model: str = "openai",
        vector_store_path: str = "./vector_store",
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize the embedding store.
        
        Args:
            embedding_model: "openai" or "huggingface"
            vector_store_path: Path to persist vector store
            openai_api_key: OpenAI API key (if using OpenAI embeddings)
        """
        self.embedding_model = embedding_model
        self.vector_store_path = vector_store_path
        self.vector_store: Optional[Chroma] = None
        
        # Initialize embeddings
        if embedding_model == "openai":
            api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var or pass openai_api_key.")
            self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        elif embedding_model == "huggingface":
            # Use a lightweight model for local embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        else:
            raise ValueError(f"Unsupported embedding model: {embedding_model}")
    
    def create_vector_store(self, documents: List[Document], persist: bool = True) -> Chroma:
        """
        Create a vector store from documents.
        
        Args:
            documents: List of Document objects to embed and store
            persist: Whether to persist the vector store to disk
            
        Returns:
            Chroma vector store instance
        """
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.vector_store_path if persist else None
        )
        return self.vector_store
    
    def load_vector_store(self) -> Chroma:
        """
        Load an existing vector store from disk.
        
        Returns:
            Chroma vector store instance
        """
        if not os.path.exists(self.vector_store_path):
            raise FileNotFoundError(f"Vector store not found at: {self.vector_store_path}")
        
        self.vector_store = Chroma(
            persist_directory=self.vector_store_path,
            embedding_function=self.embeddings
        )
        return self.vector_store
    
    def add_documents(self, documents: List[Document]):
        """
        Add new documents to existing vector store.
        
        Args:
            documents: List of Document objects to add
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Call create_vector_store() first.")
        
        self.vector_store.add_documents(documents)
    
    def get_vector_store(self) -> Optional[Chroma]:
        """Get the current vector store instance."""
        return self.vector_store

