"""
Step 1.4 - Retriever
Fetch top-K chunks for a given question.
"""

from typing import List, Optional
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_community.vectorstores import Chroma


class RAGRetriever:
    """Retrieve relevant document chunks for a question."""
    
    def __init__(self, vector_store: Chroma, top_k: int = 3):
        """
        Initialize the retriever.
        
        Args:
            vector_store: Chroma vector store instance
            top_k: Number of top chunks to retrieve
        """
        self.vector_store = vector_store
        self.top_k = top_k
        
        # Create retriever from vector store
        self.retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k}
        )
    
    def retrieve(self, question: str, top_k: Optional[int] = None) -> List[Document]:
        """
        Retrieve top-K relevant chunks for a question.
        
        Args:
            question: The question to retrieve chunks for
            top_k: Number of chunks to retrieve (overrides default if provided)
            
        Returns:
            List of retrieved Document objects
        """
        if top_k is not None and top_k != self.top_k:
            # Update retriever if top_k changed
            temp_retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": top_k}
            )
            retrieved_docs = temp_retriever.invoke(question)
        else:
            retrieved_docs = self.retriever.invoke(question)
        
        return retrieved_docs
    
    def retrieve_with_scores(self, question: str, top_k: Optional[int] = None) -> List[tuple]:
        """
        Retrieve chunks with similarity scores.
        
        Args:
            question: The question to retrieve chunks for
            top_k: Number of chunks to retrieve (overrides default if provided)
            
        Returns:
            List of tuples (Document, score)
        """
        k = top_k if top_k is not None else self.top_k
        docs_with_scores = self.vector_store.similarity_search_with_score(question, k=k)
        return docs_with_scores
    
    def update_top_k(self, top_k: int):
        """
        Update the number of chunks to retrieve.
        
        Args:
            top_k: New top_k value
        """
        self.top_k = top_k
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k}
        )
    
    def concept_exists_in_corpus(self, concept: str) -> bool:
        """
        Check if a concept exists anywhere in the corpus by searching and checking if it appears in text.
        
        Args:
            concept: The concept to search for
        
        Returns:
            True if concept exists in corpus, False otherwise
        """
        try:
            # Search with high k to check if concept exists anywhere
            docs_with_scores = self.vector_store.similarity_search_with_score(concept, k=100)
            if not docs_with_scores:
                return False
            
            # Check if the concept word actually appears in any of the retrieved documents
            concept_lower = concept.lower()
            for doc, _ in docs_with_scores[:20]:  # Check top 20 results
                if concept_lower in doc.page_content.lower():
                    return True
            
            # Also check if we got reasonably good similarity matches (concept might be semantically related)
            # If top result has distance < 0.5, it's likely related content exists
            if docs_with_scores:
                _, top_score = docs_with_scores[0]
                # Lower distance = better match, threshold of 0.7 means decent similarity
                if top_score < 0.7:
                    return True
            
            return False
        except Exception:
            # If search fails, assume concept doesn't exist
            return False
    
    def check_concepts_in_corpus(self, concepts: List[str]) -> dict:
        """
        Check which concepts exist in the corpus vs are truly missing.
        
        Args:
            concepts: List of concepts to check
        
        Returns:
            Dictionary with:
            - concepts_in_corpus: List of concepts that exist
            - concepts_missing_from_corpus: List of concepts that don't exist
        """
        concepts_in_corpus = []
        concepts_missing_from_corpus = []
        
        for concept in concepts:
            if self.concept_exists_in_corpus(concept):
                concepts_in_corpus.append(concept)
            else:
                concepts_missing_from_corpus.append(concept)
        
        return {
            "concepts_in_corpus": concepts_in_corpus,
            "concepts_missing_from_corpus": concepts_missing_from_corpus
        }

