from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid
from langchain_core.documents import Document

from .root_cause_oracle import RootCauseOracle
from .evaluator import RAGEvaluator


class RAGOracle:
    """
    Simplified high-level interface for RAG failure diagnostics.
    
    Provides a simple diagnose() method that accepts minimal inputs and handles
    evaluation and signal formatting internally.
    """
    
    def __init__(
        self,
        query_history_file: Optional[str] = None,
        embeddings=None,
        generator=None
    ):
        """
        Initialize RAGOracle.
        
        Args:
            query_history_file: Optional path to query history file.
                               Defaults to "./query_history.json"
            embeddings: Optional embedding model for auto-evaluation.
                       If not provided, evaluation must be provided in diagnose() calls.
            generator: Optional generator for LLM-as-a-Judge evaluation (more accurate).
        """
        query_history_file = query_history_file or "./query_history.json"
        self.oracle = RootCauseOracle(query_history_file=query_history_file)
        self.embeddings = embeddings
        self.generator = generator
        self.evaluator = None
        if embeddings:
            self.evaluator = RAGEvaluator(embeddings=embeddings, generator=generator)
    
    def diagnose(
        self,
        query: str,
        answer: str,
        chunks: Union[List[Document], List[Dict[str, Any]], List[str]],
        config: Optional[Dict[str, Any]] = None,
        evaluation: Optional[Dict[str, Any]] = None,
        query_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Diagnose RAG query execution and identify root causes.
        
        Args:
            query: User's question/query
            answer: Generated answer from RAG system
            chunks: Retrieved document chunks. Can be:
                   - List of LangChain Documents
                   - List of dicts with "page_content" and optionally "metadata"
                   - List of strings (will be converted to Documents)
            config: Optional system configuration dict with keys like:
                   - top_k: Number of chunks retrieved
                   - temperature: LLM temperature
                   - chunk_size: Chunk size used
            evaluation: Optional pre-computed evaluation results.
                       If not provided and embeddings available, will auto-evaluate.
            query_id: Optional query identifier. If not provided, will generate one.
        
        Returns:
            Dictionary with diagnosis results including:
            - query_id: Query identifier
            - question: Original query
            - root_causes: List of identified root causes
            - primary_failure: Highest priority root cause
            - outcome: "SUCCESS", "SUCCESS_WITH_RISK", or "FAILURE"
        """
        query_id = query_id or f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        config = config or {}
        
        chunks = self._normalize_chunks(chunks)
        
        if not evaluation:
            if self.evaluator:
                evaluation = self.evaluator.evaluate_all(
                    question=query,
                    answer=answer,
                    retrieved_chunks=chunks
                )
            else:
                raise ValueError(
                    "Evaluation not provided and no embeddings available for auto-evaluation. "
                    "Either provide evaluation results in diagnose() or initialize RAGOracle with embeddings."
                )
        
        signals = {
            "query_id": query_id,
            "question": query,
            "answer": answer,
            "retrieved_chunks": chunks,
            "evaluation": evaluation,
            "query_feasibility": None,
            "cost_optimization": None,
            "config": config,
            "corpus_concept_check": None
        }
        
        return self.oracle.analyze(signals)
    
    def get_report(self, last_n: Optional[int] = None) -> Dict[str, Any]:
        """
        Get system health report from query history.
        
        Args:
            last_n: Optional number of recent queries to analyze.
        
        Returns:
            System health report dictionary.
        """
        return self.oracle.get_report(last_n=last_n)
    
    def get_public_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get simplified public API output format.
        
        Args:
            result: Diagnosis result from diagnose() method.
        
        Returns:
            Simplified output dictionary.
        """
        return self.oracle.get_public_output(result)
    
    def _normalize_chunks(self, chunks: Union[List[Document], List[Dict[str, Any]], List[str]]) -> List[Document]:
        """Convert chunks to LangChain Document format."""
        if not chunks:
            return []
        
        if isinstance(chunks[0], Document):
            return chunks
        
        if isinstance(chunks[0], str):
            return [Document(page_content=chunk) for chunk in chunks]
        
        if isinstance(chunks[0], dict):
            normalized = []
            for chunk in chunks:
                if "page_content" in chunk:
                    doc = Document(
                        page_content=chunk["page_content"],
                        metadata=chunk.get("metadata", {})
                    )
                else:
                    doc = Document(page_content=str(chunk))
                normalized.append(doc)
            return normalized
        
        raise ValueError(f"Unsupported chunk type: {type(chunks[0])}")

