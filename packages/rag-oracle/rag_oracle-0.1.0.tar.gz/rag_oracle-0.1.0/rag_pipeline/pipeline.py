"""
Main RAG Pipeline Orchestrator
Connects all components: Loader → Chunker → Embeddings → Retriever → Generator
"""

import json
import os
from typing import List, Optional, Union, Dict, Any
from pathlib import Path
from langchain_core.documents import Document
from hashlib import md5

from .document_loader import DocumentLoader
from .chunker import DocumentChunker
from .embeddings import EmbeddingStore
from .retriever import RAGRetriever
from .tracer import RAGTracer
from .generator import RAGGenerator
from .evaluator import RAGEvaluator
from .answer_intent_classifier import AnswerIntentClassifier
from .failure_detector import FailureDetector
from .conflict_resolver import ConflictResolver
from .exact_failure_point import ExactFailurePointDetector
from .failure_attribution import FailureAttributionEngine
from .phase8_recommender import Phase8Recommender
from .self_healer import SelfHealer
# New debugging phases (A-D)
from .query_feasibility_analyzer import QueryFeasibilityAnalyzer
from .failure_surface_mapper import FailureSurfaceMapper
from .counterfactual_fix_generator import CounterfactualFixGenerator
from .fix_impact_estimator import FixImpactEstimator
from .root_cause_oracle import RootCauseOracle


class RAGPipeline:
    """
    Complete RAG pipeline that orchestrates all components.
    
    Flow: Question → Retrieved Docs → Answer
    """
    
    def __init__(
        self,
        # Document loading
        document_source: Optional[Union[str, Path]] = None,
        
        # Chunking
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        
        # Embeddings
        embedding_model: str = "huggingface",  # Default to huggingface since Groq doesn't have embeddings
        vector_store_path: str = "./vector_store",
        openai_api_key: Optional[str] = None,  # For OpenAI embeddings (if embedding_model="openai")
        
        # Retrieval
        top_k: int = 3,
        
        # Generation
        model_type: Optional[str] = None,  # None = auto-detect (OpenAI priority > Groq)
        model_name: Optional[str] = None,  # None = auto-select based on model_type
        temperature: float = 0.7,
        groq_api_key: Optional[str] = None,  # For Groq API (auto-detected if available)
        system_prompt: Optional[str] = None,
        
        # Tracing (Phase 2)
        enable_tracing: bool = True,
        log_dir: str = "./logs",
        
        # Evaluation (Phase 3)
        enable_evaluation: bool = True,
        enable_failure_detection: bool = True,
        enable_exact_failure_point: bool = True,
        enable_conflict_resolution: bool = True,
        enable_failure_attribution: bool = True,
        enable_phase8: bool = True,
        enable_self_heal: bool = True
    ):
        """
        Initialize the RAG pipeline.
        
        Args:
            document_source: Path to documents (file or directory) to load
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
            embedding_model: "openai" or "huggingface" (default: "huggingface")
            vector_store_path: Path to persist vector store
            openai_api_key: OpenAI API key (if using OpenAI)
            top_k: Number of top chunks to retrieve
            model_type: "openai", "groq", "auto", or None (auto-detect, default: None)
                       Priority: OpenAI > Groq if both available
            model_name: Name of the LLM model (default: auto-selected)
            temperature: Temperature for generation
            groq_api_key: Groq API key (if using Groq)
            system_prompt: Custom system prompt
        """
        # Initialize components
        self.document_loader = DocumentLoader()
        self.chunker = DocumentChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.embedding_store = EmbeddingStore(
            embedding_model=embedding_model,
            vector_store_path=vector_store_path,
            openai_api_key=openai_api_key
        )
        self.retriever: Optional[RAGRetriever] = None
        self.generator = RAGGenerator(
            model_type=model_type,
            model_name=model_name,
            temperature=temperature,
            openai_api_key=openai_api_key,
            groq_api_key=groq_api_key,
            system_prompt=system_prompt
        )
        
        # Initialize tracer (Phase 2)
        self.tracer = RAGTracer(log_dir=log_dir, enable_logging=enable_tracing)
        
        # Initialize evaluator (Phase 3)
        self.enable_evaluation = enable_evaluation
        if enable_evaluation:
            self.evaluator = RAGEvaluator(self.embedding_store.embeddings)
            self.answer_intent_classifier = AnswerIntentClassifier()
        else:
            self.evaluator = None
            self.answer_intent_classifier = None

        # Phase 4 - Failure Detection
        self.enable_failure_detection = enable_failure_detection
        if enable_failure_detection and self.evaluator:
            self.failure_detector = FailureDetector()
        else:
            self.failure_detector = None
        self.enable_exact_failure_point = enable_exact_failure_point
        self.exact_failure_point_detector = (
            ExactFailurePointDetector() if enable_exact_failure_point else None
        )
        self.enable_conflict_resolution = enable_conflict_resolution
        self.conflict_resolver = (
            ConflictResolver() if enable_conflict_resolution else None
        )
        self.enable_failure_attribution = enable_failure_attribution
        self.failure_attribution_engine = (
            FailureAttributionEngine() if enable_failure_attribution else None
        )
        self.enable_phase8 = enable_phase8
        self.phase8_recommender = (
            Phase8Recommender(lambda: self.retriever, self.evaluator, lambda: self.generator) if enable_phase8 else None
        )
        self.enable_self_heal = enable_self_heal
        self.self_healer = (
            SelfHealer(lambda: self.retriever, self.evaluator, lambda: self.generator) if enable_self_heal else None
        )
        
        # New debugging phases (A-D) - Always enabled when evaluation is enabled
        # These are diagnostic tools, not auto-fixing features
        if enable_evaluation:
            self.query_feasibility_analyzer = QueryFeasibilityAnalyzer(self.embedding_store.embeddings, self.retriever)
            self.failure_surface_mapper = FailureSurfaceMapper()
            self.counterfactual_fix_generator = CounterfactualFixGenerator()
            self.fix_impact_estimator = FixImpactEstimator()
            from .cost_optimizer import CostOptimizer
            self.cost_optimizer = CostOptimizer()
        else:
            self.query_feasibility_analyzer = None
            self.failure_surface_mapper = None
            self.counterfactual_fix_generator = None
            self.fix_impact_estimator = None
        
        self.root_cause_oracle = RootCauseOracle(query_history_file=str(Path(log_dir) / "query_history.json"))
        
        # Configuration - use actual model_type and model_name from generator (after auto-detection)
        self.top_k = top_k
        self.config = {
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "top_k": top_k,
            "temperature": temperature,
            "embedding_model": embedding_model,
            "model_type": self.generator.model_type,  # Actual model type used (after auto-detection)
            "model_name": getattr(self.generator, 'model_name', model_name or "auto-selected")  # Actual model name used
        }
        
        # Store document source for later checks
        self.document_source = document_source
        
        # Load documents if source provided
        if document_source:
            self._load_or_build_vector_store(document_source)
    
    def _get_vector_store_metadata_path(self) -> Path:
        """Get path to vector store metadata file."""
        return Path(self.embedding_store.vector_store_path) / "rag_config.json"
    
    def _get_document_hash(self, source: Union[str, Path]) -> str:
        """
        Generate a hash of document files to detect changes.
        
        Args:
            source: Path to documents (file or directory)
            
        Returns:
            MD5 hash string
        """
        source_path = Path(source)
        hasher = md5()
        
        if source_path.is_file():
            # Single file - use modification time and size
            stat = source_path.stat()
            hasher.update(f"{source_path}{stat.st_mtime}{stat.st_size}".encode())
        elif source_path.is_dir():
            # Directory - hash all files
            files = sorted(source_path.rglob("*"))
            for file_path in files:
                if file_path.is_file():
                    stat = file_path.stat()
                    hasher.update(f"{file_path.relative_to(source_path)}{stat.st_mtime}{stat.st_size}".encode())
        
        return hasher.hexdigest()
    
    def _get_stored_config(self) -> Optional[dict]:
        """
        Load stored vector store configuration.
        
        Returns:
            Stored config dict or None if not found
        """
        metadata_path = self._get_vector_store_metadata_path()
        if not metadata_path.exists():
            return None
        
        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def _save_vector_store_config(self, source: Union[str, Path], document_hash: str):
        """
        Save vector store configuration metadata.
        
        Args:
            source: Path to documents
            document_hash: Hash of document files
        """
        metadata_path = self._get_vector_store_metadata_path()
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            "chunk_size": self.config["chunk_size"],
            "chunk_overlap": self.config["chunk_overlap"],
            "embedding_model": self.config["embedding_model"],
            "document_source": str(source),
            "document_hash": document_hash
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _should_rebuild_vector_store(self, source: Union[str, Path]) -> bool:
        """
        Check if vector store needs to be rebuilt.
        
        Args:
            source: Path to documents
            
        Returns:
            True if rebuild is needed, False otherwise
        """
        # Check if vector store exists
        vector_store_exists = os.path.exists(self.embedding_store.vector_store_path)
        if not vector_store_exists:
            return True
        
        # Load stored config
        stored_config = self._get_stored_config()
        if not stored_config:
            return True
        
        # Check if chunking config changed
        if (stored_config.get("chunk_size") != self.config["chunk_size"] or
            stored_config.get("chunk_overlap") != self.config["chunk_overlap"]):
            return True
        
        # Check if embedding model changed
        if stored_config.get("embedding_model") != self.config["embedding_model"]:
            return True
        
        # Check if documents changed
        current_doc_hash = self._get_document_hash(source)
        if stored_config.get("document_hash") != current_doc_hash:
            return True
        
        # Check if document source changed
        if stored_config.get("document_source") != str(source):
            return True
        
        return False
    
    def _load_or_build_vector_store(self, source: Union[str, Path], force_rebuild: bool = False):
        """
        Load existing vector store or build new one if needed.
        
        Args:
            source: Path to documents (file or directory)
            force_rebuild: Force rebuild even if vector store exists
        """
        if not force_rebuild and not self._should_rebuild_vector_store(source):
            # Load existing vector store
            print(f"Loading existing vector store from: {self.embedding_store.vector_store_path}")
            try:
                vector_store = self.embedding_store.load_vector_store()
                self.retriever = RAGRetriever(vector_store, top_k=self.top_k)
                print("Vector store loaded successfully!")
                return
            except Exception as e:
                print(f"Failed to load vector store: {e}")
                print("Rebuilding vector store...")
        
        # Build new vector store
        self.load_and_index_documents(source, persist=True)
        
        # Save config metadata
        document_hash = self._get_document_hash(source)
        self._save_vector_store_config(source, document_hash)
    
    def load_and_index_documents(self, source: Union[str, Path], persist: bool = True):
        """
        Load documents, chunk them, and create vector store.
        
        Args:
            source: Path to documents (file or directory)
            persist: Whether to persist vector store to disk
        """
        print(f"Loading documents from: {source}")
        documents = self.document_loader.load(source)
        print(f"Loaded {len(documents)} documents")
        
        print("Chunking documents...")
        chunks = self.chunker.chunk_documents(documents)
        print(f"Created {len(chunks)} chunks")
        
        print("Creating embeddings and vector store...")
        vector_store = self.embedding_store.create_vector_store(chunks, persist=persist)
        print(f"Vector store created at: {self.embedding_store.vector_store_path}")
        
        # Initialize retriever
        self.retriever = RAGRetriever(vector_store, top_k=self.top_k)
        print("RAG pipeline ready!")
    
    def load_existing_vector_store(self):
        """
        Load an existing vector store from disk.
        """
        print(f"Loading vector store from: {self.embedding_store.vector_store_path}")
        vector_store = self.embedding_store.load_vector_store()
        self.retriever = RAGRetriever(vector_store, top_k=self.top_k)
        print("Vector store loaded!")
    
    def query(self, question: str, top_k: Optional[int] = None, custom_prompt: Optional[str] = None, trace_entry: Dict[str, Any] = None, attempt: int = 1) -> dict:
        """
        Query the RAG pipeline with a question.
        
        Args:
            question: User question
            top_k: Number of chunks to retrieve (overrides config)
            custom_prompt: Custom prompt template (overrides config)
            trace_entry: Existing trace entry (for chaining)
            attempt: Auto-correction attempt number
            
        Returns:
            Dictionary with answer, retrieved_chunks, evaluation, failure_detection, etc.
        """
        if self.retriever is None:
            raise ValueError("No vector store loaded. Call load_and_index_documents() or load_existing_vector_store() first.")
        
        # Retrieve relevant chunks
        k = top_k if top_k is not None else self.top_k
        raw_chunks = self.retriever.retrieve(question, top_k=k)
        
        # Deduplicate chunks based on content hash (Issue 4)
        seen_hashes = set()
        retrieved_chunks = []
        for chunk in raw_chunks:
            # Use hash of first 200 chars to identify duplicates
            content_hash = md5(chunk.page_content[:200].encode()).hexdigest()
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                retrieved_chunks.append(chunk)
        
        # Log deduplication signal if chunks were removed
        dedup_ratio = (len(raw_chunks) - len(retrieved_chunks)) / len(raw_chunks) if raw_chunks else 0
        
        # Generate answer (now returns answer and prompt)
        answer, full_prompt = self.generator.generate(question, retrieved_chunks, custom_prompt)
        
        # Get system prompt
        system_prompt = self.generator.system_prompt
        
        # Log the query (Phase 2)
        trace_entry = self.tracer.log_query(
            question=question,
            prompt=full_prompt,
            system_prompt=system_prompt,
            retrieved_chunks=retrieved_chunks,
            answer=answer,
            config=self.get_config()
        )
        
        # Issue 4: Add dedup signal to trace
        trace_entry["dedup_ratio"] = round(dedup_ratio, 2)
        trace_entry["raw_chunk_count"] = len(raw_chunks)
        
        # Evaluate (Phase 3) - NO BLAME, ONLY SIGNALS
        evaluation_results = None
        if self.enable_evaluation and self.evaluator:
            evaluation_results = self.evaluator.evaluate_all(
                question=question,
                answer=answer,
                retrieved_chunks=retrieved_chunks
            )
        
        result = {
            "question": question,
            "answer": answer,
            "retrieved_chunks": retrieved_chunks,
            "num_chunks": len(retrieved_chunks),
            "top_k": k,
            "dedup_ratio": round(dedup_ratio, 2), # Issue 4
            "trace_id": trace_entry["query_id"],  # Phase 2: Return trace ID
            "trace_entry": trace_entry  # Phase 2: Include full trace entry
        }
        
        # Add evaluation results (Phase 3)
        if evaluation_results:
            result["evaluation"] = evaluation_results
        
        # NEW: Answer Intent Classification (after Phase 3, before Phase 4)
        # This prevents misclassifying correct abstentions as failures
        answer_intent = None
        if self.answer_intent_classifier and evaluation_results:
            answer_intent = self.answer_intent_classifier.classify(answer, evaluation_results)
            result["answer_intent"] = answer_intent
            
            # SHORT-CIRCUIT: If CorrectAbstention or FullAnswer, skip failure detection
            if not answer_intent.get("should_continue_pipeline", True):
                result["resolution_type"] = answer_intent["intent"]
                
                # Issue Fix: Call Oracle logging
                signals = {
                    "query_id": result.get("trace_id", "unknown"),
                    "question": question,
                    "evaluation": evaluation_results,
                    "query_feasibility": None,
                    "cost_optimization": None,
                    "retrieved_chunks": retrieved_chunks,
                    "answer": answer,
                    "config": self.config,
                    "corpus_concept_check": None
                }
                oracle_result = self.root_cause_oracle.analyze(signals)
                result["root_causes"] = oracle_result.get("root_causes", [])

                # IMPORTANT: Persist the success result to the trace log
                if trace_entry and "query_id" in trace_entry:
                     self.tracer.update_trace(trace_entry["query_id"], result.copy())
                return result
        
        # EARLY SUCCESS CHECK: If all metrics are good, skip phases 4-6
        if evaluation_results:
            faith_data = evaluation_results.get("faithfulness", {})
            faithfulness = faith_data.get("faithfulness_factual", faith_data.get("faithfulness", 0.0))
            recall = evaluation_results.get("context_recall", {}).get("context_recall", 0.0)
            relevance = evaluation_results.get("relevance", {}).get("relevance", 0.0)
            
            # If all metrics are >= 0.7, it's a clear success - no need to run diagnostics
            if faithfulness >= 0.7 and recall >= 0.7 and relevance >= 0.7:
                result["resolution_type"] = "Success"
                
                # Issue Fix: Must call Oracle to log success history!
                signals = {
                    "query_id": result.get("trace_id", "unknown"),
                    "question": question,
                    "evaluation": evaluation_results,
                    "query_feasibility": None,
                    "cost_optimization": None,
                    "retrieved_chunks": retrieved_chunks,
                    "answer": answer,
                    "config": self.config,
                    "corpus_concept_check": None
                }
                oracle_result = self.root_cause_oracle.analyze(signals)
                result["root_causes"] = oracle_result.get("root_causes", [])
                
                # IMPORTANT: Persist the success result to the trace log
                if trace_entry and "query_id" in trace_entry:
                     self.tracer.update_trace(trace_entry["query_id"], result.copy())
                return result
        
        # NEW: Phase A - Query Feasibility Analysis (Debugging diagnostic)
        query_feasibility = None
        if self.query_feasibility_analyzer and evaluation_results:
            query_feasibility = self.query_feasibility_analyzer.analyze(
                question, evaluation_results, answer, retrieved_chunks
            )
            result["query_feasibility"] = query_feasibility
            
            # AUTO-CORRECTION LOGIC
            # AUTO-CORRECTION LOGIC
            if attempt == 1 and query_feasibility and query_feasibility.get("feasibility") == "TyposDetected":
                evidence = query_feasibility.get("evidence", {})
                suspected = evidence.get("suspected_typos", [])
                
                if suspected:
                    corrected_question = question
                    correction_log = []
                    
                    for item in suspected:
                        # item format: "wrong -> right"
                        if "->" in item:
                            wrong, right = item.split("->")
                            wrong = wrong.strip()
                            right = right.strip()
                            # Simply replace the wrong word with the right one
                            # Using case-insensitive replacement would be better, but simple replace works for now
                            import re
                            corrected_question = re.sub(re.escape(wrong), right, corrected_question, flags=re.IGNORECASE)
                            correction_log.append(f"{wrong} -> {right}")
                    
                    if corrected_question != question:
                        # Silent correction
                        
                        # Recursive call with attempt=2
                        corrected_result = self.query(corrected_question, attempt=2)
                        
                        # Add note to result so user knows
                        corrected_result["original_query"] = question
                        corrected_result["auto_corrected_from"] = correction_log
                        
                        # Return essential keys from corrected result but keep trace of original?
                        # Actually, better to just return the corrected result to the user
                        return corrected_result

        if self.enable_failure_detection and self.failure_detector and evaluation_results:
            result["failure_detection"] = self.failure_detector.detect(
                evaluation_results
            )

        if (
            self.enable_exact_failure_point
            and self.exact_failure_point_detector
            and result.get("failure_detection")
            and evaluation_results
        ):
            result["exact_failure_point"] = self.exact_failure_point_detector.detect(
                evaluation_results,
                result["failure_detection"]["failure_hypothesis"],
                self.config
            )

        corpus_concept_check = None
        missing_concepts = evaluation_results.get("context_recall", {}).get("missing_concepts", []) if evaluation_results else []
        if missing_concepts and self.retriever:
            try:
                corpus_concept_check = self.retriever.check_concepts_in_corpus(missing_concepts)
            except Exception:
                corpus_concept_check = None
        
        if (
            self.enable_conflict_resolution
            and self.conflict_resolver
            and evaluation_results
            and result.get("failure_detection")
        ):
            result["conflict_resolution"] = self.conflict_resolver.resolve(
                evaluation_results,
                result["failure_detection"]["failure_hypothesis"],
                answer_intent=answer_intent,
                query_feasibility=query_feasibility,
                corpus_concept_check=corpus_concept_check
            )
            
            # SHORT-CIRCUIT: Handle special resolution types
            final_component = result["conflict_resolution"].get("final_component")
            
            if final_component == "Success":
                result["resolution_type"] = "Success"
                return result
            
            if final_component == "ImprovementOpportunity":
                result["resolution_type"] = "ImprovementOpportunity"
                # Continue to Phase 7-8 for recommendations, but skip self-heal
                # (improvements are optional, not critical)
        
        # NEW: Phase B - Failure Surface Mapping (Debugging diagnostic)
        failure_surface = None
        if self.failure_surface_mapper and evaluation_results:
            failure_surface_result = self.failure_surface_mapper.map(
                evaluation_results,
                query_feasibility=query_feasibility,
                answer_intent=answer_intent,
                conflict_resolution=result.get("conflict_resolution"),
                num_chunks=len(retrieved_chunks),
                chunk_size=self.config.get("chunk_size", 500)
            )
            result["failure_surface"] = failure_surface_result
            failure_surface = failure_surface_result.get("failure_surface")
        
        # NEW: Phase C - Counterfactual Fix Generation (Debugging diagnostic)
        # NEW: Phase C - Counterfactual Fix Generation (MOVED TO BATCH/ANALYTICS - DISABLED RUNTIME)
        # if self.counterfactual_fix_generator and evaluation_results:
        #     counterfactual_result = self.counterfactual_fix_generator.generate(...)
        
        # NEW: Phase D - Fix Impact Estimation (MOVED TO BATCH/ANALYTICS - DISABLED RUNTIME)
        # if self.fix_impact_estimator and evaluation_results and counterfactual_fix:
        #     impact_estimate = self.fix_impact_estimator.estimate(...)
        
        # NEW: Phase E - Cost Optimization (Debugging diagnostic)
        if hasattr(self, 'cost_optimizer') and self.cost_optimizer and retrieved_chunks:
            result["cost_optimization"] = self.cost_optimizer.analyze(
                question, 
                retrieved_chunks, 
                evaluation_results, 
                self.config
            )

        if (
            self.enable_failure_attribution
            and self.failure_attribution_engine
            and result.get("failure_detection")
            and result.get("exact_failure_point")
            and result.get("conflict_resolution")
        ):
            result["failure_attribution"] = self.failure_attribution_engine.attribute(
                result["failure_detection"],
                result["exact_failure_point"],
                result["conflict_resolution"],
                evaluation_results=evaluation_results,
                failure_surface=result.get("failure_surface"),
                query_feasibility=query_feasibility
            )

        self_heal_data = None
        if (
            self.enable_phase8
            and self.phase8_recommender
            and evaluation_results
            and result.get("failure_detection")
        ):
            result["phase8_recommendation"] = self.phase8_recommender.recommend(
                question,
                evaluation_results,
                self.config,
                result.get("failure_attribution"),  # Use Phase 7 attribution if available
                result["failure_detection"],  # Fallback to Phase 4 detection
                baseline_chunks=retrieved_chunks,
                conflict_resolution=result.get("conflict_resolution")  # Pass for corpus concept checks
            )

            # GATED SELF-HEAL: Only run for actual failures, not PartialAnswer or ImprovementOpportunity
            should_self_heal = False
            
            if answer_intent:
                intent_type = answer_intent.get("intent")
                # Self-heal for: HallucinatedAnswer, HallucinatedAbstention
                # NOT for: PartialAnswer, CorrectAbstention, FullAnswer
                should_self_heal = intent_type in ["HallucinatedAnswer", "HallucinatedAbstention"]
            elif result.get("conflict_resolution"):
                # Also self-heal for specific component failures (Retrieval, Generation, Prompt)
                final_component = result["conflict_resolution"].get("final_component")
                should_self_heal = final_component in ["Retrieval", "Generation", "Prompt"]
            
            if (
                self.enable_self_heal
                and self.self_healer
                and "recommended_fix" in result["phase8_recommendation"]
                and should_self_heal  # NEW GATE
            ):
                self_heal_data = self.self_healer.heal(
                    question,
                    result["phase8_recommendation"]["recommended_fix"],
                    evaluation_results,
                    baseline_chunks=retrieved_chunks,
                    experiment_table=result["phase8_recommendation"].get("experiment_table")
                )

        if self_heal_data:
            result["phase9_self_heal"] = self_heal_data
        
        signals = {
            "query_id": result.get("trace_id", "unknown"),
            "question": question,
            "evaluation": evaluation_results,
            "query_feasibility": query_feasibility,
            "cost_optimization": result.get("cost_optimization"),
            "retrieved_chunks": retrieved_chunks,
            "answer": answer,
            "config": self.config,
            "corpus_concept_check": corpus_concept_check
        }
        
        oracle_result = self.root_cause_oracle.analyze(signals)
        result["root_causes"] = oracle_result.get("root_causes", [])
        
        if trace_entry and "query_id" in trace_entry:
             self.tracer.update_trace(trace_entry["query_id"], result.copy())
             
        return result
    
    def get_config(self) -> dict:
        """Get current pipeline configuration."""
        return self.config.copy()
    
    def update_top_k(self, top_k: int):
        """Update the number of chunks to retrieve."""
        self.top_k = top_k
        self.config["top_k"] = top_k
        if self.retriever:
            self.retriever.update_top_k(top_k)
    
    def update_temperature(self, temperature: float):
        """Update the generation temperature."""
        self.config["temperature"] = temperature
        self.generator.update_temperature(temperature)
    
    def update_system_prompt(self, system_prompt: str):
        """Update the system prompt."""
        self.generator.update_system_prompt(system_prompt)

