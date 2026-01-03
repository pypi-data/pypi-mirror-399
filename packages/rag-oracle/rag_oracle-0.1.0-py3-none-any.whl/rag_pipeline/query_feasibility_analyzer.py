"""
Phase A: Query Feasibility Analyzer
Determines if a query is answerable by ANY RAG system given the corpus.
This is a debugging signal, not a UX feature.
"""

from typing import Dict, Any, List
import re


class QueryFeasibilityAnalyzer:
    """
    Analyzes whether a query is feasible to answer given corpus constraints.
    
    Feasibility Types:
    - Answerable: Query can be answered with available information
    - OverConstrained: Query has conflicting or impossible constraints
    - UnderSpecified: Query is too vague to answer precisely
    - OutOfScope: Query asks about topics not in corpus
    """
    
    # Constraint indicators
    SCOPE_CONSTRAINTS = [
        "all", "every", "each", "entire", "whole", "complete", "fully",
        "comprehensive", "exhaustive", "total", "absolute", "overall",
        "full list", "entire list", "complete list", "everything",
        "anything and everything", "no exceptions", "without exception",
        "across all", "covering all", "cover every", "include all",
        "all possible", "every possible", "every single",
        "globally", "universally", "in all cases", "for all",
        "end-to-end", "100%", "entirely", "from start to end"
    ]

    # 🔹 Format / output constraints (often conflict with scope)
    FORMAT_CONSTRAINTS = [
        "one sentence", "single sentence", "one line",
        "two sentences", "three sentences",
        "brief", "very brief", "short", "very short", "concise",
        "summarize", "summary only", "tl;dr",
        "in one word", "in two words", "in three words",
        "in X words", "under X words", "less than X words",
        "exactly X words", "max X words", "no more than X words",
        "bullet points only", "no bullets",
        "paragraph only", "single paragraph",
        "table format", "json format", "yaml format",
        "step by step", "steps only",
        "without explanation", "no explanation",
        "answer only", "final answer only"
    ]

    # 🔹 Enumeration / counting requests (often cause underspecification)
    ENUMERATION_REQUESTS = [
        "list", "list all", "enumerate", "enumeration",
        "count", "how many", "number of",
        "give me all", "name all", "show all",
        "what are the", "which are the",
        "identify all", "provide all",
        "full breakdown", "complete breakdown",
        "all types of", "all kinds of",
        "categories of", "types of",
        "examples of", "every example",
        "all instances", "all cases",
        "items", "entries", "records",
        "top X", "bottom X", "first X", "last X"
    ]
    
    def __init__(self, embeddings=None, retriever=None):
        """Initialize the analyzer."""
        self.embeddings = embeddings
        self.retriever = retriever
    
    def _detect_scope_constraint(self, question: str) -> Dict[str, Any]:
        """Detect if query requests exhaustive coverage."""
        question_lower = question.lower()
        
        for constraint in self.SCOPE_CONSTRAINTS:
            if constraint in question_lower:
                return {
                    "has_scope_constraint": True,
                    "constraint_type": "exhaustive_coverage",
                    "keyword": constraint
                }
        
        return {"has_scope_constraint": False}
    
    def _detect_format_constraint(self, question: str) -> Dict[str, Any]:
        """Detect if query has strict format requirements."""
        question_lower = question.lower()
        
        for constraint in self.FORMAT_CONSTRAINTS:
            if constraint in question_lower:
                return {
                    "has_format_constraint": True,
                    "constraint_type": "response_length",
                    "keyword": constraint
                }
        
        return {"has_format_constraint": False}
    
    def _detect_enumeration_request(self, question: str) -> Dict[str, Any]:
        """Detect if query requests enumeration."""
        question_lower = question.lower()
        
        for keyword in self.ENUMERATION_REQUESTS:
            if keyword in question_lower:
                return {
                    "has_enumeration": True,
                    "keyword": keyword
                }
        
        return {"has_enumeration": False}
    
    def _check_corpus_structure(
        self, 
        missing_concepts: List[str],
        context_recall: float
    ) -> Dict[str, Any]:
        """Analyze if corpus structure supports the query."""
        
        # If many concepts are missing, corpus may not cover topic
        if len(missing_concepts) > 3:
            return {
                "corpus_coverage": "insufficient",
                "missing_concept_count": len(missing_concepts)
            }
        
        # If recall is very low, corpus doesn't have structured info
        if context_recall < 0.4:
            return {
                "corpus_coverage": "fragmented",
                "recall_score": context_recall
            }
        
        return {
            "corpus_coverage": "adequate",
            "recall_score": context_recall
        }
    
    def analyze(
        self,
        question: str,
        evaluation_results: Dict[str, Any],
        answer: str,
        retrieved_chunks: List[Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze query feasibility.
        
        Args:
            question: The user's query
            evaluation_results: Phase 3 evaluation metrics
            answer: The generated answer
            retrieved_chunks: List of retrieved documents (needed for typo detection)
             
        Returns:
            Dictionary with feasibility status
        """
        
        # Extract metrics
        recall = evaluation_results.get("context_recall", {}).get("context_recall", 0.0)
        missing_concepts = evaluation_results.get("context_recall", {}).get("missing_concepts", [])
        relevance = evaluation_results.get("relevance", {}).get("relevance", 0.0)
        
        # Detect constraints
        scope_constraint = self._detect_scope_constraint(question)
        format_constraint = self._detect_format_constraint(question)
        enumeration = self._detect_enumeration_request(question)
        corpus_structure = self._check_corpus_structure(missing_concepts, recall)
        
        # Decision logic
        
        # Check Typos First (High Priority)
        import difflib
        
        # Build dictionary from content AND metadata (e.g. Titles)
        text_sources = []
        if retrieved_chunks:
            for c in retrieved_chunks:
                text_sources.append(c.page_content)
                # Add metadata values that are strings
                if hasattr(c, "metadata") and c.metadata:
                    for v in c.metadata.values():
                        if isinstance(v, str):
                            text_sources.append(v)
                            
        chunk_text = " ".join(text_sources)
        chunk_words = set(re.findall(r'\w+', chunk_text.lower()))
        
        # Check ALL query words, not just missing concepts
        # This catches typos even if the retriever/LLM compensated for them
        q_words = re.findall(r'\w+', question.lower())
        stop_words = {"what", "how", "why", "who", "the", "a", "an", "in", "on", "of", "to", "is", "are", "do", "does", "did", "can", "could", "would", "should", "summarize", "explain", "describe", "tell", "me", "about", "one", "word"}
        
        suspected_typos = []
        for w in q_words:
            if w in stop_words or len(w) < 4: continue
            if w in chunk_words: continue
            
            # check if similar word exists in chunks
            matches = difflib.get_close_matches(w, chunk_words, n=1, cutoff=0.8)
            if matches:
                suspected_typos.append(f"{w} -> {matches[0]}")
        
        if suspected_typos:
             return {
                "feasibility": "TyposDetected",
                "confidence": 0.95,
                "evidence": {
                    "suspected_typos": suspected_typos,
                    "missing_concepts": missing_concepts
                },
                "recommendation": f"Correct spelling in query: {', '.join(suspected_typos)}"
            }
        
        # Case 1: OverConstrained (conflicting requirements)
        if (scope_constraint["has_scope_constraint"] and 
            format_constraint["has_format_constraint"]):
            return {
                "feasibility": "OverConstrained",
                "confidence": 0.90,
                "evidence": {
                    "requested_scope": scope_constraint["keyword"],
                    "response_constraint": format_constraint["keyword"],
                    "conflict": "Cannot provide exhaustive coverage in constrained format"
                },
                "recommendation": (
                    f"Remove either '{scope_constraint['keyword']}' (scope) or "
                    f"'{format_constraint['keyword']}' (format) constraint"
                )
            }
        
        # Case 2: OutOfScope (corpus doesn't have the information)
        if corpus_structure["corpus_coverage"] == "insufficient" and recall < 0.5:
            return {
                "feasibility": "OutOfScope",
                "confidence": 0.85,
                "evidence": {
                    "corpus_coverage": corpus_structure["corpus_coverage"],
                    "missing_concepts": missing_concepts,
                    "recall_score": recall
                },
                "recommendation": (
                    "Query asks about topics not well-covered in corpus. "
                    "Consider adding relevant documents or rephrasing query."
                )
            }
        
        # Case 3: UnderSpecified (too vague)
        if len(question.split()) < 5 and relevance < 0.6:
            return {
                "feasibility": "UnderSpecified",
                "confidence": 0.75,
                "evidence": {
                    "query_length": len(question.split()),
                    "relevance_score": relevance,
                    "issue": "Query is too vague to retrieve precise information"
                },
                "recommendation": "Add more specific details or context to the query"
            }
        
        # Case 4: Answerable (no major constraints or issues)
        return {
            "feasibility": "Answerable",
            "confidence": 0.80,
            "evidence": {
                "corpus_coverage": corpus_structure["corpus_coverage"],
                "recall_score": recall,
                "constraints_detected": {
                    "scope": scope_constraint["has_scope_constraint"],
                    "format": format_constraint["has_format_constraint"],
                    "enumeration": enumeration["has_enumeration"]
                }
            },
            "recommendation": "Query is feasible. Proceed with normal debugging if issues arise."
        }
