"""
Phase 3 - Basic Evaluation Signals
Measure faithfulness, relevance, and context recall.
NO BLAME, ONLY SIGNALS
"""

import re
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .concept_type_separator import ConceptTypeSeparator


class RAGEvaluator:
    """Evaluate RAG responses using basic signals: faithfulness, relevance, context recall."""

    META_REASONING_KEYWORDS = [
        "does not contain enough information",
        "context does not mention",
        "cannot be answered",
        "cannot answer",
        "not enough information",
        "information is missing",
        "missing from the context",
        "insufficient information",
        "provided context",
        "lack sufficient detail",
        "no evidence in the context",
        "unable to determine",
    ]
    
    
    def __init__(self, embeddings, generator=None):
        """
        Initialize the evaluator.
        
        Args:
            embeddings: Embedding model to use for similarity calculations
            generator: Optional RAGGenerator instance for LLM-as-a-Judge (higher accuracy)
        """
        self.embeddings = embeddings
        self.generator = generator
        self.concept_separator = ConceptTypeSeparator()
    
    def evaluate_faithfulness_llm(self, answer: str, retrieved_chunks: List[Document]) -> Dict[str, Any]:
        """
        Evaluate faithfulness using LLM-as-a-Judge (More accurate, slower).
        """
        if not self.generator:
            return {"faithfulness": 0.0, "error": "No generator provided for LLM eval"}
            
        context_text = "\n\n".join([c.page_content for c in retrieved_chunks])
        
        prompt = f"""
        You are an expert fact-checking AI. 
        Your task is to verify if the following ANSWER is strictly supported by the CONTEXT.
        
        CONTEXT:
        {context_text}
        
        ANSWER:
        {answer}
        
        INSTRUCTIONS:
        1. Break the answer into individual factual claims.
        2. For each claim, check if it is explicitly supported by the CONTEXT.
        3. Count unsupported claims.
        4. Return a JSON object with:
           - "faithfulness_score": (0.0 to 1.0)
           - "unsupported_claims": [list of strings]
           
        JSON OUTPUT ONLY.
        """
        
        try:
            response = self.generator.generate_raw(prompt)
            # Simple parsing (in production use structured output)
            import json
            # find first { and last }
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end != -1:
                data = json.loads(response[start:end])
                return {
                    "faithfulness": data.get("faithfulness_score", 0.0),
                    "faithfulness_factual": data.get("faithfulness_score", 0.0),
                    "unsupported_claims": data.get("unsupported_claims", []),
                    "unsupported_factual_claims": data.get("unsupported_claims", []),
                    "method": "llm_judge"
                }
        except Exception as e:
            print(f"LLM Eval failed: {e}")
            
        return {"faithfulness": 0.0, "error": "LLM Eval failed"}
    
    def _split_into_claims(self, text: str) -> List[str]:
        """
        Split text into individual claims (sentences).
        
        Args:
            text: Text to split
            
        Returns:
            List of claim strings
        """
        # Split by sentence endings
        sentences = re.split(r'[.!?]+', text)
        # Clean and filter empty sentences
        claims = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        return claims
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """
        Extract key concepts from text (simple keyword extraction).
        
        Args:
            text: Text to extract concepts from
            
        Returns:
            List of key concept strings
        """
        # Simple approach: extract significant words (nouns, important terms)
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
                     'could', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
                     'what', 'which', 'who', 'where', 'when', 'why', 'how'}
        
        # Extract words (simple tokenization)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        # Filter stop words and get unique significant words
        concepts = list(set([w for w in words if w not in stop_words and len(w) > 3]))
        # Limit to top concepts (longer words are often more specific)
        concepts = sorted(concepts, key=len, reverse=True)[:10]
        return concepts
    
    def _compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts using embeddings.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        try:
            emb1 = np.array(self.embeddings.embed_query(text1)).reshape(1, -1)
            emb2 = np.array(self.embeddings.embed_query(text2)).reshape(1, -1)
            similarity = cosine_similarity(emb1, emb2)[0][0]
            return float(similarity)
        except Exception as e:
            # Fallback: simple word overlap if embedding fails
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            if len(words1) == 0 or len(words2) == 0:
                return 0.0
            overlap = len(words1 & words2) / len(words1 | words2)
            return float(overlap)
    
    def _is_meta_reasoning(self, claim: str, domain_terms: List[str]) -> bool:
        """
        Determine if a claim is meta-reasoning (discusses ability to answer) instead of a factual assertion.
        """
        claim_lower = claim.lower()
        if not any(keyword in claim_lower for keyword in self.META_REASONING_KEYWORDS):
            return False
        if not domain_terms:
            return True
        # If the claim introduces specific domain terms, treat it as factual despite meta phrasing
        return not any(term in claim_lower for term in domain_terms if term)
    
    def evaluate_faithfulness(
        self,
        answer: str,
        retrieved_chunks: List[Document],
        similarity_threshold: float = 0.5,
        question: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Step 3.1 - Faithfulness (Hallucination)
        Check if every sentence in the answer is supported by retrieved docs.
        
        Args:
            answer: The generated answer
            retrieved_chunks: List of retrieved document chunks
            similarity_threshold: Minimum similarity to consider a claim supported
            
        Returns:
            Dictionary with faithfulness score and unsupported claims
        """
        if not answer or not retrieved_chunks:
            return {
                "faithfulness": 0.0,
                "unsupported_claims": []
            }
        
        # Split answer into claims
        claims = self._split_into_claims(answer)
        if not claims:
            return {
                "faithfulness": 1.0,  # Empty answer is technically faithful
                "faithfulness_factual": 1.0,
                "faithfulness_meta": 1.0,
                "unsupported_claims": [],
                "unsupported_factual_claims": [],
                "unsupported_meta_claims": [],
                "claim_counts": {"total": 0, "factual": 0, "meta": 0},
                "meta_claims": []
            }
        
        # Combine all retrieved chunks into context
        context = "\n\n".join([chunk.page_content for chunk in retrieved_chunks])
        question_terms = []
        if question:
            try:
                question_terms = [term.lower() for term in self._extract_key_concepts(question)]
            except Exception:
                question_terms = []
        
        # Check each claim against context
        unsupported_factual = []
        unsupported_meta = []
        factual_claims = []
        meta_claims = []
        
        for claim in claims:
            if self._is_meta_reasoning(claim, question_terms):
                meta_claims.append(claim)
                continue  # Meta statements shouldn't penalize factual faithfulness
            
            factual_claims.append(claim)
            # Compute similarity between claim and context
            similarity = self._compute_similarity(claim, context)
            if similarity < similarity_threshold:
                unsupported_factual.append({
                    "claim": claim,
                    "similarity": similarity
                })
        
        # Calculate faithfulness score (percentage of supported claims)
        faithfulness_factual = (
            1.0 - (len(unsupported_factual) / len(factual_claims))
            if factual_claims else 1.0
        )
        faithfulness_meta = (
            1.0 - (len(unsupported_meta) / len(meta_claims))
            if meta_claims else 1.0
        )
        
        result = {
            "faithfulness": round(faithfulness_factual, 2),
            "faithfulness_factual": round(faithfulness_factual, 2),
            "faithfulness_meta": round(faithfulness_meta, 2),
            "unsupported_claims": unsupported_factual,
            "unsupported_factual_claims": unsupported_factual,
            "unsupported_meta_claims": unsupported_meta,
            "claim_counts": {
                "total": len(claims),
                "factual": len(factual_claims),
                "meta": len(meta_claims)
            },
            "meta_claims": meta_claims
        }
        
        return result
    
    def evaluate_relevance(
        self, 
        question: str, 
        answer: str
    ) -> Dict[str, Any]:
        """
        Step 3.2 - Relevance (Intent Match)
        Check if the answer actually answers the question.
        
        Args:
            question: The original question
            answer: The generated answer
            
        Returns:
            Dictionary with relevance score
        """
        if not question or not answer:
            return {
                "relevance": 0.0
            }
        
        # Compute similarity between question and answer
        similarity = self._compute_similarity(question, answer)
        
        return {
            "relevance": round(similarity, 2)
        }
    
    def evaluate_context_recall(
        self, 
        question: str, 
        retrieved_chunks: List[Document]
    ) -> Dict[str, Any]:
        """
        Step 3.3 - Context Recall (Retriever Coverage)
        Check if retrieved docs contain the needed info.
        
        Args:
            question: The original question
            retrieved_chunks: List of retrieved document chunks
            
        Returns:
            Dictionary with context_recall score and missing concepts
        """
        if not question or not retrieved_chunks:
            return {
                "context_recall": 0.0,
                "missing_concepts": [],
                "all_concepts": []
            }
        
        # Extract key concepts from question
        all_concepts = self._extract_key_concepts(question)
        
        # CRITICAL FIX: Separate knowledge concepts from instruction tokens with confidence
        # Issue 1: Context Recall = 0.0 but Missing Concepts = []
        separated = self.concept_separator.separate_concepts(all_concepts)
        knowledge_meta = separated["knowledge_metadata"]
        
        if not knowledge_meta:
            return {
                "context_recall": 1.0,  # No knowledge concepts to check
                "missing_concepts": [],
                "all_concepts": all_concepts
            }
        
        # Combine all retrieved chunks into context
        context = "\n\n".join([chunk.page_content for chunk in retrieved_chunks])
        context_lower = context.lower()
        
        # Check which concepts are present in context
        missing_concepts = []
        weighted_found_sum = 0.0
        total_confidence_sum = sum(k["confidence"] for k in knowledge_meta)
        
        for k_item in knowledge_meta:
            concept = k_item["text"]
            confidence = k_item["confidence"]
            concept_lower = concept.lower()
            
            # Check if concept appears in context (simple substring match)
            if concept_lower in context_lower:
                weighted_found_sum += confidence
            else:
                # Fallback: check similar words
                context_words = context_lower.split()
                similar_found = any(
                    concept_lower[:4] in word or word[:4] in concept_lower 
                    for word in context_words if len(word) > 3
                )
                if similar_found:
                    weighted_found_sum += (confidence * 0.5) # Partial credit for fuzzy match
                else:
                    missing_concepts.append(concept)
        
        # Calculate weighted recall score
        context_recall = weighted_found_sum / total_confidence_sum if total_confidence_sum > 0 else 1.0
        
        return {
            "context_recall": round(context_recall, 2),
            "missing_concepts": missing_concepts,
            "all_concepts": all_concepts,
            "knowledge_meta": knowledge_meta # Return meta for debugging
        }
    
    def evaluate_all(
        self,
        question: str,
        answer: str,
        retrieved_chunks: List[Document],
        similarity_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Evaluate all three signals: faithfulness, relevance, context_recall.
        
        Args:
            question: The original question
            answer: The generated answer
            retrieved_chunks: List of retrieved document chunks
            similarity_threshold: Minimum similarity for faithfulness evaluation
            
        Returns:
            Dictionary with all evaluation results
        """
        faithfulness = self.evaluate_faithfulness(
            answer,
            retrieved_chunks,
            similarity_threshold,
            question=question
        )
        relevance = self.evaluate_relevance(question, answer)
        context_recall = self.evaluate_context_recall(question, retrieved_chunks)
        
        return {
            "faithfulness": faithfulness,
            "relevance": relevance,
            "context_recall": context_recall
        }

