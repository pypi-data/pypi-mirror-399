"""
Phase 2 - Tracing and Logging
Capture evidence for each query to make RAG debuggable.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from langchain_core.documents import Document


class RAGTracer:
    """Trace and log all query information for debugging and evaluation."""
    
    def __init__(self, log_dir: str = "./logs", enable_logging: bool = True):
        """
        Initialize the tracer.
        
        Args:
            log_dir: Directory to save log files
            enable_logging: Whether to enable logging (default: True)
        """
        self.log_dir = Path(log_dir)
        self.enable_logging = enable_logging
        
        # Create log directory if it doesn't exist
        if self.enable_logging:
            self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def _serialize_chunks(self, chunks: List[Document]) -> List[Dict[str, Any]]:
        """
        Serialize document chunks to JSON-serializable format.
        
        Args:
            chunks: List of Document objects
            
        Returns:
            List of dictionaries with chunk content and metadata
        """
        serialized = []
        for chunk in chunks:
            serialized.append({
                "content": chunk.page_content,
                "metadata": chunk.metadata if hasattr(chunk, 'metadata') else {}
            })
        return serialized
    
    def log_query(
        self,
        question: str,
        prompt: str,
        system_prompt: Optional[str],
        retrieved_chunks: List[Document],
        answer: str,
        config: Dict[str, Any],
        query_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log a query with all its information.
        
        Args:
            question: The question asked
            prompt: The full prompt used (including context)
            system_prompt: The system prompt used
            retrieved_chunks: List of retrieved document chunks
            answer: The generated answer
            config: Configuration used (top_k, chunk_size, temperature, etc.)
            query_id: Optional unique ID for this query (auto-generated if not provided)
            
        Returns:
            Dictionary containing all logged information
        """
        if not query_id:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            query_id = f"query_{timestamp}"
        
        # Build the trace entry
        trace_entry = {
            "query_id": query_id,
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "prompt": {
                "system_prompt": system_prompt,
                "full_prompt": prompt
            },
            "retrieved_chunks": self._serialize_chunks(retrieved_chunks),
            "answer": answer,
            "config": config,
            "metadata": {
                "num_chunks": len(retrieved_chunks),
                "total_chunk_length": sum(len(chunk.page_content) for chunk in retrieved_chunks)
            }
        }
        
        # Save to file if logging is enabled
        if self.enable_logging:
            log_file = self.log_dir / f"{query_id}.json"
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(trace_entry, f, indent=2, ensure_ascii=False)
        
        return trace_entry
    
    def load_query(self, query_id: str) -> Dict[str, Any]:
        """
        Load a logged query by ID.
        
        Args:
            query_id: The query ID to load
            
        Returns:
            Dictionary containing the query information
        """
        log_file = self.log_dir / f"{query_id}.json"
        if not log_file.exists():
            raise FileNotFoundError(f"Query log not found: {log_file}")
        
        with open(log_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_queries(self) -> List[str]:
        """
        List all query IDs in the log directory.
        
        Returns:
            List of query IDs (sorted by filename)
        """
        if not self.log_dir.exists():
            return []
        
        query_files = sorted(self.log_dir.glob("query_*.json"))
        return [f.stem for f in query_files]
    
    def get_all_queries(self) -> List[Dict[str, Any]]:
        """
        Load all logged queries.
        
        Returns:
            List of all query dictionaries
        """
        query_ids = self.list_queries()
        return [self.load_query(qid) for qid in query_ids]

    def update_trace(self, query_id: str, updates: Dict[str, Any]) -> None:
        """
        Update an existing trace with new information (e.g. diagnostics metrics).
        """
        if not self.enable_logging:
            return
            
        log_file = self.log_dir / f"{query_id}.json"
        
        if not log_file.exists():
            return
            
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Merge updates into the trace dictionary
            # Exclude raw retrieved_chunks if they are Documents, as they are already logged via _serialize_chunks
            if "retrieved_chunks" in updates and isinstance(updates["retrieved_chunks"], list) and len(updates["retrieved_chunks"]) > 0:
                 if not isinstance(updates["retrieved_chunks"][0], dict):
                     del updates["retrieved_chunks"]

            data.update(updates)
            
            def json_serial(obj):
                """JSON serializer for objects not serializable by default json code"""
                if hasattr(obj, 'to_dict'):
                    return obj.to_dict()
                if hasattr(obj, '__dict__'):
                    return obj.__dict__
                return str(obj)

            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=json_serial)
                
        except Exception as e:
            print(f"Failed to update trace {query_id}: {e}")

