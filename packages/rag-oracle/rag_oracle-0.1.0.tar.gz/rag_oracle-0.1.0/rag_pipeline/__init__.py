"""
RAG Pipeline - Phase 1, 2 & 3
A RAG pipeline for document retrieval, generation, tracing, and evaluation.
"""

from .pipeline import RAGPipeline
from .tracer import RAGTracer
from .evaluator import RAGEvaluator
from .failure_attribution import FailureAttributionEngine
from .phase8_recommender import Phase8Recommender
from .root_cause_oracle import RootCauseOracle
from .rag_oracle import RAGOracle
from .config import RAGConfig, DEFAULT_CONFIG

__all__ = [
    'RAGPipeline',
    'RAGTracer',
    'RAGEvaluator',
    'FailureAttributionEngine',
    'Phase8Recommender',
    'RootCauseOracle',
    'RAGOracle',
    'RAGConfig',
    'DEFAULT_CONFIG'
]

__version__ = '0.1.0'

