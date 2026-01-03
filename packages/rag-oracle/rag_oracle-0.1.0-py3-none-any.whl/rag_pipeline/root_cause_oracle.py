from typing import Dict, Any, List, Optional
import json
import re
from pathlib import Path
from collections import Counter
from datetime import datetime


class RootCauseOracle:
    NON_DOMAIN_TERMS={
    # Expanded question & instruction words
    "elaborate", "outline", "breakdown", "walkthrough", "explanation",
    "explanations", "clarification", "interpret", "interpretation",
    "summarize", "summarized", "summarization", "brief", "briefly",
    "deep", "deeper", "in-depth", "high-level",

    # More generic verbs
    "check", "checking", "verify", "verified", "confirm", "confirmed",
    "compare", "comparing", "contrast", "contrasting",
    "analyze", "analysis", "review", "reviewed",
    "list", "listed", "listing", "add", "added", "remove", "removed",
    "update", "updated", "change", "changed",

    # Expanded generic adjectives
    "clear", "unclear", "easy", "hard", "difficult",
    "useful", "useless", "helpful", "unhelpful",
    "fast", "slow", "quick", "efficient", "inefficient",
    "accurate", "inaccurate", "correct", "incorrect",
    "complete", "incomplete", "full", "partial",

    # More time / frequency fillers
    "often", "sometimes", "usually", "rarely", "never", "always",
    "early", "earlier", "late", "later", "soon", "eventually",
    "before", "after", "during", "while", "meanwhile",

    # Expanded quantity & degree
    "enough", "plenty", "extra", "less", "more", "most", "least",
    "almost", "about", "around", "approximately", "exactly",
    "nearly", "roughly", "slightly", "highly",

    # Opinion & evaluation fillers
    "opinion", "view", "perspective", "thought", "thoughts",
    "belief", "believe", "consider", "considered",
    "recommend", "recommended", "suggest", "suggested",
    "rating", "rank", "ranking",

    # Conversational & intent fillers
    "want", "wanted", "need", "needed", "trying",
    "looking", "planning", "thinking",
    "shouldnt", "couldnt", "wouldnt", "doesnt", "dont",
    "cant", "wont", "isnt", "arent",

    # Meta / formatting / structure
    "point", "points", "topic", "topics",
    "title", "heading", "headings", "subheading",
    "note", "notes", "remark", "remarks",
    "example-based", "case", "cases",

    # Platform / medium neutral terms
    "online", "offline", "website", "site", "platform",
    "system", "tool", "tools", "application", "app",
    "service", "services", "feature", "features"
}
    
    def __init__(self, query_history_file: str = "./query_history.json"):
        self.query_history = []
        self.query_history_file = Path(query_history_file)
        self.fix_history_file = Path(str(self.query_history_file.parent / "fix_history.json"))
        self._load_query_history()
        self._load_fix_history()
    
    def _filter_domain_concepts(self, missing_concepts: List[str]) -> List[str]:
        filtered = [c for c in missing_concepts if c.lower() not in self.NON_DOMAIN_TERMS]
        return filtered
    
    def _get_user_explanation_and_unfixable(self, rule_type: str, fix: str, evidence: Dict[str, Any], question: str = "") -> tuple[str, bool]:
        is_unfixable = False
        user_explanation = ""
        
        if rule_type == "Corpus Coverage":
            is_unfixable = True
            missing = evidence.get("missing_concepts", [])
            missing_str = ", ".join(missing[:5])
            user_explanation = f"Your system failed because the required information does not exist in your documents. No retrieval or prompt tuning can fix this. You must add documents covering: {missing_str}."
        
        elif rule_type == "User Query":
            user_explanation = "Your query contains spelling errors that prevent accurate retrieval. Correct the typos and resubmit the query."
        
        elif rule_type == "User Query (Ambiguous Grammar)":
            user_explanation = "Your query is written as a statement rather than a question, which can confuse the retrieval system. Rephrase it as an explicit question."
        
        elif rule_type == "User Query Constraints":
            user_explanation = "Your query has strict formatting requirements (e.g., 'list exactly 5 items') that may be too rigid. Consider relaxing the format constraints or splitting into multiple queries."
        
        elif rule_type == "Retrieval Configuration":
            is_unfixable = False
            top_k = evidence.get("current_top_k", 3)
            suggested = evidence.get("suggested_top_k", top_k + 2)
            user_explanation = f"Your retrieval is not fetching enough relevant chunks. The system retrieved {top_k} chunks, but needs more. Increase top_k to {suggested} or adjust chunk_size to capture more context."
        
        elif rule_type == "Retrieval Noise":
            user_explanation = "Your retrieval is returning irrelevant chunks that don't match the query. This creates noise in the answer. Improve chunk filtering, reduce top_k, or refine your chunking strategy."
        
        elif rule_type == "Embedding Model":
            is_unfixable = False
            user_explanation = "Your embedding model is not capturing the semantic relationships needed for this domain. The same concepts exist in your corpus but aren't being matched. Consider switching to a domain-specific embedding model or fine-tuning your current model."
        
        elif rule_type == "Prompt Design":
            user_explanation = "Your prompt is not effectively utilizing the retrieved context. The retrieval is working well, but the generation prompt needs improvement to better synthesize the retrieved information."
        
        elif rule_type == "Hallucination Risk" or rule_type == "Generation Control":
            user_explanation = "Your system is generating answers that contain information not present in the retrieved documents. Lower the temperature to reduce creativity, or enforce extractive answering to only use information from the context."
        
        elif rule_type == "Cost Inefficiency":
            user_explanation = "Your system is retrieving more chunks than necessary, wasting tokens and cost. Reduce top_k to only retrieve what's needed for the answer."
        
        elif rule_type == "Systemic Drift":
            user_explanation = "Your system performance has degraded over time. Review recent configuration changes, corpus updates, or model changes that may have caused this drift."
        
        else:
            user_explanation = f"System issue detected: {rule_type}. {fix}"
        
        question_lower = question.lower() if question else ""
        real_time_keywords = ["current", "now", "today", "latest", "recent", "live", "real-time", "up to date", "current price", "current status"]
        if any(kw in question_lower for kw in real_time_keywords):
            is_unfixable = True
            user_explanation = "Your query requests real-time or current information that cannot be answered from static documents. This requires data updates or integration with live data sources."
        
        return user_explanation, is_unfixable
    
    def _is_declarative_statement(self, question: str) -> bool:
        question = question.strip()
        if not question:
            return False
        
        question_lower = question.lower()
        
        if question.endswith('?'):
            return False
        
        question_words = question_lower.split()
        if len(question_words) < 3:
            return False
        
        declarative_starters = {"this", "that", "it", "fear", "anxiety", "the", "a", "an"}
        if question_words[0] in declarative_starters:
            return True
        
        has_verb_early = any(word in question_words[:3] for word in ["is", "are", "was", "were", "has", "have", "does", "do"])
        if has_verb_early and not any(word in question_words for word in ["what", "how", "why", "when", "where", "who", "which", "can", "could", "should", "will"]):
            return True
        
        return False

    def analyze(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze query execution signals and identify root causes of failures.
        
        Args:
            signals: Dictionary containing:
                - query_id (str): Unique identifier for the query
                - question (str): User's question
                - answer (str): Generated answer
                - evaluation (dict): Evaluation metrics including:
                    - faithfulness (dict): Faithfulness scores and unsupported claims
                    - relevance (dict): Relevance scores
                    - context_recall (dict): Recall scores and missing concepts
                - retrieved_chunks (list): Retrieved document chunks
                - query_feasibility (dict): Query analysis (typos, grammar)
                - cost_optimization (dict): Cost metrics
                - config (dict): System configuration (top_k, temperature, etc.)
                - corpus_concept_check (dict): Corpus vs retrieval distinction analysis
        
        Returns:
            Dictionary with:
                - query_id (str): Query identifier
                - question (str): User's question
                - root_causes (list): List of identified root causes, each containing:
                    - rank (int): Priority rank
                    - type (str): Root cause type (e.g., "Corpus Coverage", "Retrieval Configuration")
                    - fix (str): Recommended fix
                    - user_explanation (str): User-friendly explanation
                    - is_unfixable (bool): Whether fix requires data/corpus changes
                    - confidence (float): Confidence score (0.0-1.0)
                    - evidence (dict): Supporting evidence
                - primary_failure (dict): Highest priority root cause
                - secondary_risk (dict, optional): Second priority root cause
                - outcome (str): "SUCCESS", "SUCCESS_WITH_RISK", or "FAILURE"
        """
        query_id = signals.get("query_id", "unknown")
        question = signals.get("question", "")
        
        evaluation_results = signals.get("evaluation", {})
        query_feasibility = signals.get("query_feasibility")
        cost_optimization = signals.get("cost_optimization")
        retrieved_chunks = signals.get("retrieved_chunks", [])
        answer = signals.get("answer", "")
        config = signals.get("config", {})
        
        root_causes = []
        
        if not evaluation_results:
            # Ensure we log this as a failure before returning
            query_record = {
                "query_id": query_id,
                "question": question,
                "timestamp": datetime.now().isoformat(),
                "root_cause": "Evaluation Missing",
                "fix": "Check Evaluator configuration",
                "confidence": 0.0,
                "cost_waste": 0.0,
                "outcome": "FAILURE"
            }
            self.query_history.append(query_record)
            self._save_query_history()
            return self._finalize_attribution([], query_id, question, cost_optimization, evaluation_results)
        
        faithfulness_data = evaluation_results.get("faithfulness", {})
        faithfulness = faithfulness_data.get("faithfulness_factual", faithfulness_data.get("faithfulness", 1.0))
        relevance = evaluation_results.get("relevance", {}).get("relevance", 0.0)
        recall = evaluation_results.get("context_recall", {}).get("context_recall", 0.0)
        missing_concepts = evaluation_results.get("context_recall", {}).get("missing_concepts", [])
        unsupported_claims = faithfulness_data.get("unsupported_factual_claims", faithfulness_data.get("unsupported_claims", []))
        
        corpus_concept_check = signals.get("corpus_concept_check")
        
        filtered_missing_concepts = self._filter_domain_concepts(missing_concepts)
        is_declarative = self._is_declarative_statement(question)
        
        rule1_result = self._rule1_typo(signals, query_feasibility, recall)
        if rule1_result:
            root_causes.append(rule1_result)
        
        rule1b_result = self._rule1b_declarative_grammar(question, faithfulness, relevance, recall, is_declarative)
        if rule1b_result:
            root_causes.append(rule1b_result)
        
        rule_metadata_result = self._rule_metadata_satisfied(answer, retrieved_chunks, faithfulness, recall, question)
        if rule_metadata_result:
            return self._finalize_attribution([], query_id, question, cost_optimization, evaluation_results)
        
        rule_silent_hallucination = self._rule_silent_hallucination(answer, retrieved_chunks, faithfulness, recall, question)
        if rule_silent_hallucination:
            root_causes.insert(0, rule_silent_hallucination)
        
        rule2_result = self._rule2_out_of_scope(filtered_missing_concepts, corpus_concept_check, recall, faithfulness, answer, retrieved_chunks, question)
        if rule2_result:
            root_causes.append(rule2_result)
        
        corpus_coverage_fired = any(c.get("type") == "Corpus Coverage" for c in root_causes)
        
        if corpus_coverage_fired:
            root_causes = [c for c in root_causes if c.get("type") == "Corpus Coverage"]
        
        rule3_result = self._rule3_over_constrained(query_feasibility, faithfulness, relevance, question)
        if rule3_result and not corpus_coverage_fired:
            root_causes.append(rule3_result)
        
        if not corpus_coverage_fired:
            rule4_result = self._rule4_retrieval_recall_deficiency(recall, filtered_missing_concepts, corpus_concept_check, config, answer, retrieved_chunks, question)
            if rule4_result:
                root_causes.append(rule4_result)
            # if len(root_causes) >= 3 limit removed to ensure logging
        
        rule5_result = self._rule5_retrieval_noise(recall, relevance, retrieved_chunks, answer, config, question)
        if rule5_result and not corpus_coverage_fired:
            root_causes.append(rule5_result)
        
        if not corpus_coverage_fired:
            rule6_result = self._rule6_embedding_mismatch(recall, filtered_missing_concepts, corpus_concept_check, config, root_causes, question)
            if rule6_result:
                root_causes.append(rule6_result)
        
        rule7_result = self._rule7_prompt_mismatch(recall, faithfulness, relevance, recall, question)
        if rule7_result and not corpus_coverage_fired:
            root_causes.append(rule7_result)
        
        rule8_result = self._rule8_hallucination(faithfulness, unsupported_claims, config, answer, question)
        if rule8_result and not corpus_coverage_fired:
            root_causes.append(rule8_result)
        
        rule9_result = self._rule9_cost_inefficiency(cost_optimization, retrieved_chunks, answer, evaluation_results, config, question)
        if rule9_result and not corpus_coverage_fired:
            root_causes.append(rule9_result)
        
        rule10_result = self._rule10_systemic_drift(signals)
        if rule10_result:
            root_causes.append(rule10_result)
        
        if not root_causes:
            silent_hallucination = self._rule_silent_hallucination(answer, retrieved_chunks, faithfulness, recall, question)
            if silent_hallucination:
                root_causes.append(silent_hallucination)
        
        partial_answer_result = self._rule_partial_answer_acceptable(answer, retrieved_chunks, faithfulness, recall, missing_concepts, corpus_concept_check)
        if partial_answer_result and not any(c.get("type") in ["Corpus Coverage", "Retrieval Configuration", "Hallucination Risk", "Generation Control"] for c in root_causes):
            root_causes.append(partial_answer_result)
        
        result = self._finalize_attribution(root_causes, query_id, question, cost_optimization, evaluation_results)
        
        outcome = self._classify_outcome(evaluation_results, root_causes)
        failure_type = root_causes[0].get("type") if root_causes else None
        
        primary_fix = root_causes[0].get("fix") if root_causes else None
        fix_id = self._generate_fix_id(primary_fix, failure_type) if primary_fix else None
        
        active_fix_id = self._detect_active_fix(config)
        if not active_fix_id and fix_id:
            explicit_fix_id = signals.get("applied_fix_id")
            if explicit_fix_id:
                active_fix_id = explicit_fix_id
        
        if fix_id and not any(f.get("fix_id") == fix_id and not f.get("applied_at") for f in self.fix_history):
            fix_record = {
                "fix_id": fix_id,
                "rule_type": failure_type,
                "fix": primary_fix,
                "config_before": self._extract_config_params(config, fix_id),
                "recommended_at": datetime.now().isoformat(),
                "applied_at": None
            }
            self.fix_history.append(fix_record)
            self._save_fix_history()
        
        query_record = {
            "query_id": query_id,
            "question": question,
            "timestamp": datetime.now().isoformat(),
            "root_cause": failure_type,
            "fix": primary_fix,
            "confidence": root_causes[0].get("confidence") if root_causes else None,
            "cost_waste": cost_optimization.get("wasted_cost", 0.0) if cost_optimization else 0.0,
            "total_cost": cost_optimization.get("total_cost", 0.0) if cost_optimization else 0.0,
            "outcome": outcome,
            "active_fix_id": active_fix_id
        }
        
        self.query_history.append(query_record)
        self._save_query_history()
        
        result["outcome"] = outcome
        return result
    
    def _is_plural_singular_diff(self, word1: str, word2: str) -> bool:
        word1_lower = word1.lower().strip()
        word2_lower = word2.lower().strip()
        
        if word1_lower == word2_lower:
            return False
        
        if word1_lower.endswith('s') and word1_lower[:-1] == word2_lower:
            return True
        
        if word2_lower.endswith('s') and word2_lower[:-1] == word1_lower:
            return True
        
        if word1_lower.endswith('es') and word1_lower[:-2] == word2_lower:
            return True
        
        if word2_lower.endswith('es') and word2_lower[:-2] == word1_lower:
            return True
        
        if word1_lower.endswith('ies') and word2_lower.endswith('y'):
            if word1_lower[:-3] == word2_lower[:-1]:
                return True
        
        if word2_lower.endswith('ies') and word1_lower.endswith('y'):
            if word2_lower[:-3] == word1_lower[:-1]:
                return True
        
        return False
    
    def _is_severe_misspelling(self, word1: str, word2: str) -> bool:
        word1_lower = word1.lower().strip()
        word2_lower = word2.lower().strip()
        
        if self._is_plural_singular_diff(word1_lower, word2_lower):
            return False
        
        if len(word1_lower) < 4 or len(word2_lower) < 4:
            return False
        
        import difflib
        similarity = difflib.SequenceMatcher(None, word1_lower, word2_lower).ratio()
        
        if similarity < 0.7:
            return True
        
        if abs(len(word1_lower) - len(word2_lower)) > 2:
            return True
        
        return False
    
    def _rule1_typo(self, signals: Dict[str, Any], query_feasibility: Optional[Dict], recall: float) -> Optional[Dict[str, Any]]:
        if not query_feasibility:
            return None
        
        if query_feasibility.get("feasibility") == "TyposDetected":
            evidence_dict = query_feasibility.get("evidence", {})
            detected_typos = evidence_dict.get("suspected_typos", [])
            
            if not detected_typos:
                return None
            
            evaluation_results = signals.get("evaluation", {})
            faithfulness_data = evaluation_results.get("faithfulness", {})
            faithfulness = faithfulness_data.get("faithfulness_factual", faithfulness_data.get("faithfulness", 1.0))
            recall_val = evaluation_results.get("context_recall", {}).get("context_recall", 0.0)
            
            if recall_val >= 0.6 and faithfulness >= 0.7:
                return None
            
            severe_typos = []
            for typo_pair in detected_typos:
                if "->" in typo_pair:
                    wrong, right = typo_pair.split("->")
                    wrong = wrong.strip()
                    right = right.strip()
                    if self._is_severe_misspelling(wrong, right):
                        severe_typos.append(typo_pair)
            
            if not severe_typos:
                return None
            
            confidence = self._calculate_confidence(recall_val, 1.0, 0.0)
            question = signals.get("question", "")
            fix = "Correct spelling or normalize query before retrieval"
            evidence = {"detected_typos": severe_typos}
            user_explanation, is_unfixable = self._get_user_explanation_and_unfixable("User Query", fix, evidence, question)
            
            return {
                "rank": 1,
                "type": "User Query",
                "fix": fix,
                "user_explanation": user_explanation,
                "is_unfixable": is_unfixable,
                "evidence": evidence,
                "confidence": confidence
            }
        return None
    
    def _rule1b_declarative_grammar(self, question: str, faithfulness: float, relevance: float, recall: float, is_declarative: bool) -> Optional[Dict[str, Any]]:
        if is_declarative and faithfulness >= 0.7 and recall >= 0.6:
            confidence = self._calculate_confidence(recall, 0.7, 0.0)
            fix = "Normalize query into explicit question form before retrieval"
            evidence = {
                "query_form": "declarative",
                "missing_question_marker": True,
                "retrieval_relevance": recall,
                "faithfulness_score": faithfulness
            }
            user_explanation, is_unfixable = self._get_user_explanation_and_unfixable("User Query (Ambiguous Grammar)", fix, evidence, question)
            
            return {
                "rank": 1,
                "type": "User Query (Ambiguous Grammar)",
                "fix": fix,
                "user_explanation": user_explanation,
                "is_unfixable": is_unfixable,
                "evidence": evidence,
                "confidence": confidence
            }
        return None
    
    def _rule_metadata_satisfied(self, answer: str, retrieved_chunks: List, faithfulness: float, recall: float, question: str) -> bool:
        if faithfulness < 0.8:
            return False
        
        if not retrieved_chunks:
            return False
        
        metadata_fields = ["total_pages", "page_count", "pages", "author", "title", "date", "published_date", "publication_date", "isbn", "publisher"]
        question_lower = question.lower()
        
        metadata_keywords = {
    # Document structure
    "page": [
        "page", "pages", "page number", "page no", "pageno",
        "length", "total pages", "how many pages"
    ],
    "section": [
        "section", "sections", "chapter", "chapters",
        "part", "parts", "subsection", "heading"
    ],

    # Authorship & ownership
    "author": [
        "author", "authors", "writer", "written by",
        "created by", "creator", "editor", "edited by"
    ],
    "organization": [
        "organization", "company", "publisher", "institution",
        "issued by", "owned by"
    ],

    # Titles & identity
    "title": [
        "title", "document title", "book title",
        "name of the book", "name of the document",
        "document name", "file name"
    ],
    "version": [
        "version", "edition", "revised", "revision",
        "updated version", "latest version"
    ],

    # Time & publication
    "date": [
        "date", "when", "published", "publication date",
        "released", "release date", "issued",
        "created on", "last updated"
    ],
    "year": [
        "year", "which year", "published in",
        "release year"
    ],

    # Format & medium
    "format": [
        "format", "file type", "type of file",
        "pdf", "doc", "docx", "txt", "html"
    ],
    "language": [
        "language", "written in", "document language"
    ],

    # Content classification
    "topic": [
        "topic", "topics", "subject", "subjects",
        "about", "related to", "focus"
    ],
    "keywords": [
        "keyword", "keywords", "key terms",
        "tags", "labels"
    ],
    "summary": [
        "summary", "abstract", "overview",
        "short description"
    ],

    # Legal & rights
    "license": [
        "license", "licensed under", "copyright",
        "usage rights", "terms"
    ],

    # Source & traceability
    "source": [
        "source", "origin", "from where",
        "reference", "references", "citation"
    ]
}

        
        answer_lower = answer.lower()
        
        for chunk in retrieved_chunks:
            if not hasattr(chunk, "metadata") or not chunk.metadata:
                continue
            
            for key, value in chunk.metadata.items():
                key_lower = key.lower()
                if any(field in key_lower for field in metadata_fields):
                    if isinstance(value, (int, float, str)):
                        value_str = str(value)
                        if value_str.lower() in answer_lower or value_str in answer:
                            for keyword_type, keywords in metadata_keywords.items():
                                if any(kw in question_lower for kw in keywords):
                                    if keyword_type == "page" and ("page" in key_lower or "pages" in key_lower):
                                        return True
                                    elif keyword_type == "author" and "author" in key_lower:
                                        return True
                                    elif keyword_type == "title" and "title" in key_lower:
                                        return True
                                    elif keyword_type == "date" and ("date" in key_lower or "published" in key_lower):
                                        return True
        
        return False
    
    def _extract_factual_claims(self, text: str) -> Dict[str, Any]:
        numbers = re.findall(r'\b\d+\b', text)
        dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}\b', text)
        capitalized_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        return {
            "has_numbers": len(numbers) > 0,
            "has_dates": len(dates) > 0,
            "has_names": len(capitalized_names) > 2,
            "numbers": numbers,
            "dates": dates,
            "names": capitalized_names[:3]
        }
    
    def _verify_claim_grounding(self, answer: str, retrieved_chunks: List) -> float:
        if not retrieved_chunks:
            return 0.0
        
        answer_lower = answer.lower()
        context_text = " ".join([chunk.page_content.lower() for chunk in retrieved_chunks])
        
        factual_claims = self._extract_factual_claims(answer)
        verified_count = 0
        total_claims = 0
        
        if factual_claims["has_numbers"]:
            total_claims += len(factual_claims["numbers"])
            for num in factual_claims["numbers"]:
                if num in context_text or str(int(num)) in context_text:
                    verified_count += 1
        
        if factual_claims["has_dates"]:
            total_claims += len(factual_claims["dates"])
            for date in factual_claims["dates"]:
                if date in context_text:
                    verified_count += 1
        
        if factual_claims["has_names"]:
            total_claims += len(factual_claims["names"])
            for name in factual_claims["names"]:
                name_lower = name.lower()
                if name_lower in context_text:
                    verified_count += 1
        
        if total_claims == 0:
            return 1.0
        
        return verified_count / total_claims
    
    def _has_uncertainty_language(self, answer: str) -> bool:
        answer_lower = answer.lower()
        uncertainty_phrases = [
            "does not explicitly state", "cannot be inferred", "not directly mentioned",
            "does not directly answer", "not explicitly stated", "cannot be directly inferred",
            "not directly addressed", "does not directly address", "not explicitly addressed",
            "however, the context doesn't", "the context doesn't directly", "not directly answer",
            "cannot be determined from", "not clearly stated", "not explicitly provided"
        ]
        return any(phrase in answer_lower for phrase in uncertainty_phrases)
    
    def _rule_silent_hallucination(self, answer: str, retrieved_chunks: List, faithfulness: float, recall: float, question: str) -> Optional[Dict[str, Any]]:
        if self._has_uncertainty_language(answer):
            return None
        
        answer_lower = answer.lower()
        inference_phrases = ["can be inferred", "based on", "it can be", "appears to", "seems to", "likely", "probably", "suggests", "implies"]
        has_inference = any(phrase in answer_lower for phrase in inference_phrases)
        
        factual_claims = self._extract_factual_claims(answer)
        has_factual = factual_claims["has_numbers"] or factual_claims["has_dates"] or factual_claims["has_names"]
        
        if not (has_inference or has_factual):
            return None
        
        grounding_overlap = self._verify_claim_grounding(answer, retrieved_chunks)
        if grounding_overlap >= 0.5 and not has_inference:
            return None
        
        if has_inference and grounding_overlap < 0.3:
            confidence = self._calculate_confidence(recall, grounding_overlap, 0.0)
            fix = "Verify answer claims against retrieved context. If unverifiable, enforce extractive answering or abstain."
            evidence = {
                "inference_detected": True,
                "grounding_overlap": round(grounding_overlap, 2),
                "retrieval_recall": recall
            }
            user_explanation, is_unfixable = self._get_user_explanation_and_unfixable("Hallucination Risk", fix, evidence, question)
            return {
                "rank": 1,
                "type": "Hallucination Risk",
                "fix": fix,
                "user_explanation": user_explanation,
                "is_unfixable": is_unfixable,
                "evidence": evidence,
                "confidence": confidence
            }
        
        if has_factual:
            answer_tokens = len(answer.split())
            if answer_tokens >= 20:
                return None
            
            if grounding_overlap >= 0.5:
                return None
            
            confidence = self._calculate_confidence(recall, grounding_overlap, 0.0)
            fix = "Verify answer claims against retrieved context. If unverifiable, enforce extractive answering or abstain."
            evidence = {
                "answer_length_tokens": answer_tokens,
                "factual_claims_detected": {
                    "numbers": factual_claims["has_numbers"],
                    "dates": factual_claims["has_dates"],
                    "names": factual_claims["has_names"]
                },
                "grounding_overlap": round(grounding_overlap, 2),
                "retrieval_recall": recall
            }
            user_explanation, is_unfixable = self._get_user_explanation_and_unfixable("Hallucination Risk", fix, evidence, question)
            return {
                "rank": 1,
                "type": "Hallucination Risk",
                "fix": fix,
                "user_explanation": user_explanation,
                "is_unfixable": is_unfixable,
                "evidence": evidence,
                "confidence": confidence
            }
        
        return None
    
    def _calculate_confidence(self, recall: float, grounding_overlap: float, counterfactual_delta: float) -> float:
        base_confidence = (recall * 0.4) + (grounding_overlap * 0.4) + (min(counterfactual_delta, 0.2) * 0.2)
        return min(max(base_confidence, 0.0), 1.0)
    
    def _is_existence_question(self, question: str) -> bool:
        question_lower = question.lower()
        existence_patterns = [
            "does", "do", "is there", "are there", "has", "have",
            "define", "defines", "defines a", "defines the",
            "guarantee", "guarantees", "guaranteed",
            "provide", "provides", "contains", "contain",
            "include", "includes", "offer", "offers"
        ]
        return any(pattern in question_lower for pattern in existence_patterns)
    
    def _check_negation_in_chunks(self, question: str, retrieved_chunks: List) -> bool:
        if not retrieved_chunks:
            return False
        
        question_lower = question.lower()
        
        negation_keywords = [
            "no guarantee", "does not guarantee", "cannot guarantee", "no formula",
            "argues against", "rejects", "denies", "does not provide",
            "does not contain", "does not include", "does not offer",
            "no universal", "no single", "no one", "no such",
            "impossible", "cannot be", "cannot have", "cannot provide",
            "rejects the idea", "argues that", "emphasizes that there is no",
            "no guaranteed", "no guarantees", "there is no", "there are no"
        ]
        
        context_text = " ".join([chunk.page_content.lower() for chunk in retrieved_chunks])
        
        for neg_keyword in negation_keywords:
            if neg_keyword in context_text:
                question_concepts = self._extract_query_concepts(question)
                if question_concepts:
                    for concept in question_concepts[:3]:
                        if concept in context_text:
                            return True
        
        return False
    
    def _answer_contains_negation(self, answer: str, question: str) -> bool:
        answer_lower = answer.lower()
        question_lower = question.lower()
        
        negation_phrases = [
            "no guarantee", "does not guarantee", "cannot guarantee", "no formula",
            "does not provide", "does not contain", "does not include",
            "no universal", "no single", "no such", "there is no", "there are no",
            "does not define", "does not offer", "cannot be guaranteed",
            "rejects", "denies", "argues against", "emphasizes that there is no"
        ]
        
        if any(phrase in answer_lower for phrase in negation_phrases):
            question_concepts = self._extract_query_concepts(question)
            if question_concepts:
                for concept in question_concepts[:3]:
                    if concept in answer_lower:
                        return True
        
        return False
    
    def _rule2_out_of_scope(self, missing_concepts: List[str], corpus_concept_check: Optional[Dict], recall: float, faithfulness: float, answer: str, retrieved_chunks: List, question: str) -> Optional[Dict[str, Any]]:
        if self._is_existence_question(question):
            if self._check_negation_in_chunks(question, retrieved_chunks) or self._answer_contains_negation(answer, question):
                return None
        
        is_abstention = self._is_correct_abstention(answer, faithfulness)
        query_concept_overlap = self._check_query_concepts_in_chunks(question, retrieved_chunks)
        
        if is_abstention:
            if recall > 0.6 and query_concept_overlap > 0.5:
                return None
            
            concepts_missing_from_corpus = []
            if corpus_concept_check:
                concepts_missing_from_corpus = corpus_concept_check.get("concepts_missing_from_corpus", [])
            
            query_concepts = self._extract_query_concepts(question)
            filtered_missing = self._filter_domain_concepts(missing_concepts) if missing_concepts else []
            filtered_query_concepts = [c for c in query_concepts if c.lower() not in self.NON_DOMAIN_TERMS] if query_concepts else []
            
            if concepts_missing_from_corpus:
                missing_list = [c for c in concepts_missing_from_corpus if c.lower() not in self.NON_DOMAIN_TERMS]
            elif filtered_query_concepts:
                missing_list = filtered_query_concepts[:3]
            elif filtered_missing:
                missing_list = filtered_missing[:3]
            else:
                missing_list = ["requested information"]
            
            if not missing_list or missing_list == ["requested information"]:
                return None
            
            fix = f"Expand corpus. Missing: {', '.join(missing_list)}."
            
            grounding_overlap = 0.2 if query_concept_overlap < 0.5 else 0.3
            counterfactual_delta = 0.0
            confidence = self._calculate_confidence(recall, grounding_overlap, counterfactual_delta)
            evidence = {
                "missing_concepts": missing_list,
                "retrieval_delta": counterfactual_delta,
                "grounding_overlap": round(grounding_overlap, 2),
                "abstention_detected": True,
                "query_concept_overlap": round(query_concept_overlap, 2),
                "confidence_formula": f"recall({recall:.2f})*0.4 + grounding({grounding_overlap:.2f})*0.4 + delta({counterfactual_delta:.2f})*0.2"
            }
            user_explanation, is_unfixable = self._get_user_explanation_and_unfixable("Corpus Coverage", fix, evidence, question)
            
            return {
                "rank": 1,
                "type": "Corpus Coverage",
                "fix": fix,
                "user_explanation": user_explanation,
                "is_unfixable": is_unfixable,
                "evidence": evidence,
                "confidence": confidence
            }
        
        if query_concept_overlap < 0.2 and missing_concepts:
            query_concepts = self._extract_query_concepts(question)
            if query_concepts:
                concepts_missing_from_corpus = []
                if corpus_concept_check:
                    concepts_missing_from_corpus = corpus_concept_check.get("concepts_missing_from_corpus", [])
                
                filtered_missing = self._filter_domain_concepts(missing_concepts)
                filtered_query_concepts = [c for c in query_concepts if c.lower() not in self.NON_DOMAIN_TERMS]
                
                if concepts_missing_from_corpus:
                    missing_list = [c for c in concepts_missing_from_corpus if c.lower() not in self.NON_DOMAIN_TERMS]
                elif filtered_query_concepts:
                    missing_list = filtered_query_concepts[:3]
                elif filtered_missing:
                    missing_list = filtered_missing[:3]
                else:
                    missing_list = ["requested information"]
                
                if not missing_list or missing_list == ["requested information"]:
                    return None
                
                fix = f"Expand corpus. Missing: {', '.join(missing_list)}."
                
                grounding_overlap = 0.1
                counterfactual_delta = 0.0
                confidence = self._calculate_confidence(recall, grounding_overlap, counterfactual_delta)
                evidence = {
                    "missing_concepts": missing_list,
                    "retrieval_delta": counterfactual_delta,
                    "grounding_overlap": round(grounding_overlap, 2),
                    "query_concept_overlap": round(query_concept_overlap, 2),
                    "confidence_formula": f"recall({recall:.2f})*0.4 + grounding({grounding_overlap:.2f})*0.4 + delta({counterfactual_delta:.2f})*0.2"
                }
                user_explanation, is_unfixable = self._get_user_explanation_and_unfixable("Corpus Coverage", fix, evidence, question)
                
                return {
                    "rank": 1,
                    "type": "Corpus Coverage",
                    "fix": fix,
                    "user_explanation": user_explanation,
                    "is_unfixable": is_unfixable,
                    "evidence": evidence,
                    "confidence": confidence
                }
        
        if faithfulness >= 0.7:
            return None

        if not missing_concepts:
            return None
        
        factual_claims = self._extract_factual_claims(answer)
        if not (factual_claims["has_numbers"] or factual_claims["has_dates"] or factual_claims["has_names"]):
            return None
        
        question_lower = question.lower()
        groundable_keywords = ["how many", "what is", "when", "who", "where", "which", "count", "number", "date", "year"]
        asks_groundable_fact = any(kw in question_lower for kw in groundable_keywords)
        if not asks_groundable_fact:
            return None
        
        if not retrieved_chunks:
            return None
        
        context_text = " ".join([chunk.page_content.lower() for chunk in retrieved_chunks])
        numeric_overlap = False
        entity_overlap = False
        
        if factual_claims["has_numbers"]:
            for num in factual_claims["numbers"]:
                if num in context_text or str(int(num)) in context_text:
                    numeric_overlap = True
                    break
        
        if factual_claims["has_names"]:
            for name in factual_claims["names"]:
                if name.lower() in context_text:
                    entity_overlap = True
                    break
        
        if numeric_overlap or entity_overlap:
            return None
        
        concepts_missing_from_corpus = []
        if corpus_concept_check:
            concepts_missing_from_corpus = corpus_concept_check.get("concepts_missing_from_corpus", [])
        
        if concepts_missing_from_corpus or (recall < 0.3 and len(missing_concepts) > 2):
            filtered_missing = self._filter_domain_concepts(missing_concepts) if missing_concepts else []
            
            if concepts_missing_from_corpus:
                missing_list = [c for c in concepts_missing_from_corpus if c.lower() not in self.NON_DOMAIN_TERMS]
            elif filtered_missing:
                missing_list = filtered_missing[:3]
            else:
                missing_list = ["requested information"]
            
            if not missing_list or missing_list == ["requested information"]:
                return None
            
            missing_type = "metadata attribute" if "page" in question_lower or "author" in question_lower else "entity/relation"
            source = "document metadata table" if "page" in question_lower else "corpus documents"
            validation = "retrieval returns numeric value ≥1" if factual_claims["has_numbers"] else "retrieval returns entity match"
            
            fix = f"Missing {missing_type}. Source: {source}. Validation: {validation}."
            
            grounding_overlap = self._verify_claim_grounding(answer, retrieved_chunks)
            counterfactual_delta = 0.0
            confidence = self._calculate_confidence(recall, grounding_overlap, counterfactual_delta)
            evidence = {
                "missing_concepts": missing_list,
                "retrieval_delta": counterfactual_delta,
                "grounding_overlap": round(grounding_overlap, 2),
                "numeric_overlap": numeric_overlap,
                "entity_overlap": entity_overlap,
                "confidence_formula": f"recall({recall:.2f})*0.4 + grounding({grounding_overlap:.2f})*0.4 + delta({counterfactual_delta:.2f})*0.2"
            }
            user_explanation, is_unfixable = self._get_user_explanation_and_unfixable("Corpus Coverage", fix, evidence, question)
            
            return {
                "rank": 1,
                "type": "Corpus Coverage",
                "fix": fix,
                "user_explanation": user_explanation,
                "is_unfixable": is_unfixable,
                "evidence": evidence,
                "confidence": confidence
            }
        return None
    
    def _rule3_over_constrained(self, query_feasibility: Optional[Dict], faithfulness: float, relevance: float, question: str = "") -> Optional[Dict[str, Any]]:
        if not query_feasibility:
            return None
        
        feasibility = query_feasibility.get("feasibility")
        if feasibility == "OverConstrained":
            confidence = self._calculate_confidence(0.6, 0.7, 0.0)
            fix = "Relax formatting constraints or split query"
            evidence = {
                "constraint_detected": True,
                "confidence_formula": f"recall(0.60)*0.4 + grounding(0.70)*0.4 + delta(0.00)*0.2"
            }
            user_explanation, is_unfixable = self._get_user_explanation_and_unfixable("User Query Constraints", fix, evidence, question)
            
            return {
                "rank": 1,
                "type": "User Query Constraints",
                "fix": fix,
                "user_explanation": user_explanation,
                "is_unfixable": is_unfixable,
                "evidence": evidence,
                "confidence": confidence
            }
        
        if faithfulness >= 0.7 and relevance < 0.5:
            evidence_dict = query_feasibility.get("evidence", {})
            constraints = evidence_dict.get("constraints_detected", {})
            if constraints.get("format") or constraints.get("scope") or constraints.get("enumeration"):
                confidence = self._calculate_confidence(0.6, 0.5, 0.0)
                fix = "Relax formatting constraints or split query"
                evidence = {
                    "constraint_detected": True,
                    "relevance": relevance,
                    "confidence_formula": f"recall(0.60)*0.4 + grounding(0.50)*0.4 + delta(0.00)*0.2"
                }
                question = query_feasibility.get("question", "")
                user_explanation, is_unfixable = self._get_user_explanation_and_unfixable("User Query Constraints", fix, evidence, question)
                
                return {
                    "rank": 1,
                    "type": "User Query Constraints",
                    "fix": fix,
                    "user_explanation": user_explanation,
                    "is_unfixable": is_unfixable,
                    "evidence": evidence,
                    "confidence": confidence
                }
        return None
    
    def _rule4_retrieval_recall_deficiency(self, recall: float, missing_concepts: List[str], corpus_concept_check: Optional[Dict], config: Dict, answer: str, retrieved_chunks: List, question: str) -> Optional[Dict[str, Any]]:
        is_abstention = self._is_correct_abstention(answer, 1.0)
        query_concept_overlap = self._check_query_concepts_in_chunks(question, retrieved_chunks)
        
        if is_abstention and recall > 0.6 and query_concept_overlap > 0.5:
            top_k = config.get("top_k", 3)
            recall_gap = 1.0 - recall
            counterfactual_delta = min(recall_gap * 0.5, 0.3)
            grounding_overlap = 0.5
            confidence = self._calculate_confidence(recall, grounding_overlap, counterfactual_delta)
            import math
            suggested_top_k = top_k + max(1, math.ceil(counterfactual_delta * 10))
            fix = f"Increase top_k from {top_k} to {suggested_top_k} or adjust chunk_size"
            evidence = {
                "recall_score": recall,
                "counterfactual_recall_gain": counterfactual_delta,
                "query_concept_overlap": round(query_concept_overlap, 2),
                "abstention_with_high_recall": True,
                "current_top_k": top_k,
                "suggested_top_k": suggested_top_k,
                "confidence_formula": f"recall({recall:.2f})*0.4 + grounding({grounding_overlap:.2f})*0.4 + delta({counterfactual_delta:.2f})*0.2"
            }
            user_explanation, is_unfixable = self._get_user_explanation_and_unfixable("Retrieval Configuration", fix, evidence, question)
            
            return {
                "rank": 1,
                "type": "Retrieval Configuration",
                "fix": fix,
                "user_explanation": user_explanation,
                "is_unfixable": is_unfixable,
                "evidence": evidence,
                "confidence": confidence
            }
        
        if recall < 0.6 and missing_concepts:
            concepts_in_corpus = []
            if corpus_concept_check:
                concepts_in_corpus = corpus_concept_check.get("concepts_in_corpus", [])
            
            if concepts_in_corpus or (not corpus_concept_check and recall < 0.5):
                answer_tokens = len(answer.split())
                expected_length = 30
                is_short_answer = answer_tokens < expected_length
                is_abstention_check = self._is_correct_abstention(answer, 1.0)
                grounding_overlap_check = self._verify_claim_grounding(answer, retrieved_chunks)
                
                if not (is_short_answer or is_abstention_check) and grounding_overlap_check >= 0.6:
                    return None
                
                top_k = config.get("top_k", 3)
                recall_gap = 1.0 - recall
                missing_count_factor = min(len(missing_concepts) / 5.0, 1.0) if missing_concepts else 0.5
                counterfactual_delta = min(recall_gap * 0.6 + missing_count_factor * 0.1, 0.3)
                grounding_overlap = 0.5
                confidence = self._calculate_confidence(recall, grounding_overlap, counterfactual_delta)
                import math
                suggested_top_k = top_k + max(1, math.ceil(counterfactual_delta * 10))
                fix = f"Increase top_k from {top_k} to {suggested_top_k} or adjust chunk_size"
                evidence = {
                    "recall_score": recall,
                    "counterfactual_recall_gain": counterfactual_delta,
                    "current_top_k": top_k,
                    "suggested_top_k": suggested_top_k,
                    "confidence_formula": f"recall({recall:.2f})*0.4 + grounding({grounding_overlap:.2f})*0.4 + delta({counterfactual_delta:.2f})*0.2"
                }
                user_explanation, is_unfixable = self._get_user_explanation_and_unfixable("Retrieval Configuration", fix, evidence, question)
                
                return {
                    "rank": 1,
                    "type": "Retrieval Configuration",
                    "fix": fix,
                    "user_explanation": user_explanation,
                    "is_unfixable": is_unfixable,
                    "evidence": evidence,
                    "confidence": confidence
                }
        return None
    
    def _rule5_retrieval_noise(self, recall: float, relevance: float, retrieved_chunks: List, answer: str, config: Dict, question: str = "") -> Optional[Dict[str, Any]]:
        if recall >= 0.6 and relevance < 0.5:
            if not retrieved_chunks:
                return None
            
            used_chunks = self._count_used_chunks(retrieved_chunks, answer)
            unused_ratio = 1.0 - (used_chunks / len(retrieved_chunks)) if retrieved_chunks else 0.0
            
            if unused_ratio >= 0.4:
                top_k = config.get("top_k", 3)
                chunk_overlap = config.get("chunk_overlap", 50)
                grounding_overlap = 1.0 - unused_ratio
                confidence = self._calculate_confidence(recall, grounding_overlap, 0.0)
                fix = f"Reduce top_k from {top_k} or chunk_overlap from {chunk_overlap}"
                evidence = {
                    "unused_chunks_ratio": unused_ratio,
                    "relevance_drop": relevance,
                    "confidence_formula": f"recall({recall:.2f})*0.4 + grounding({grounding_overlap:.2f})*0.4 + delta(0.00)*0.2"
                }
                user_explanation, is_unfixable = self._get_user_explanation_and_unfixable("Retrieval Noise", fix, evidence, question)
                
                return {
                    "rank": 1,
                    "type": "Retrieval Noise",
                    "fix": fix,
                    "user_explanation": user_explanation,
                    "is_unfixable": is_unfixable,
                    "evidence": evidence,
                    "confidence": confidence
                }
        return None
    
    def _rule6_embedding_mismatch(self, recall: float, missing_concepts: List[str], corpus_concept_check: Optional[Dict], config: Dict, root_causes: List[Dict], question: str = "") -> Optional[Dict[str, Any]]:
        if recall >= 0.5:
            return None
        
        concepts_in_corpus = []
        if corpus_concept_check:
            concepts_in_corpus = corpus_concept_check.get("concepts_in_corpus", [])
        
        if not concepts_in_corpus:
            return None
        
        retrieval_config_fired = any(c.get("type") == "Retrieval Configuration" for c in root_causes)
        if not retrieval_config_fired:
            return None
        
        failure_count = 0
        for q in self.query_history[-10:]:
            if q.get("root_cause") == "Embedding Model":
                failure_count += 1
        
        if failure_count < 2:
            return None
        
        embedding_model = config.get("embedding_model", "huggingface")
        if embedding_model == "huggingface":
            grounding_overlap = 0.3
            counterfactual_delta = 0.1
            confidence = self._calculate_confidence(recall, grounding_overlap, counterfactual_delta)
            fix = "Switch to domain-specific embeddings"
            evidence = {
                "global_recall_trend": recall,
                "corpus_domain_tags": "general",
                "historical_failure_count": failure_count,
                "confidence_formula": f"recall({recall:.2f})*0.4 + grounding({grounding_overlap:.2f})*0.4 + delta({counterfactual_delta:.2f})*0.2"
            }
            user_explanation, is_unfixable = self._get_user_explanation_and_unfixable("Embedding Model", fix, evidence, question)
            
            return {
                "rank": 1,
                "type": "Embedding Model",
                "fix": fix,
                "user_explanation": user_explanation,
                "is_unfixable": is_unfixable,
                "evidence": evidence,
                "confidence": confidence
            }
        return None
    
    def _rule7_prompt_mismatch(self, recall: float, faithfulness: float, relevance: float, retrieval_relevance: float, question: str = "") -> Optional[Dict[str, Any]]:
        if retrieval_relevance > 0.5 and faithfulness >= 0.7 and relevance < 0.5:
            confidence = self._calculate_confidence(recall, 0.5, 0.0)
            fix = "Rewrite system prompt to enforce task alignment"
            evidence = {
                "relevance_score": relevance,
                "faithfulness_score": faithfulness,
                "retrieval_relevance": retrieval_relevance,
                "confidence_formula": f"recall({recall:.2f})*0.4 + grounding(0.50)*0.4 + delta(0.00)*0.2"
            }
            user_explanation, is_unfixable = self._get_user_explanation_and_unfixable("Prompt Design", fix, evidence, question)
            
            return {
                "rank": 1,
                "type": "Prompt Design",
                "fix": fix,
                "user_explanation": user_explanation,
                "is_unfixable": is_unfixable,
                "evidence": evidence,
                "confidence": confidence
            }
        return None
    
    def _is_correct_abstention(self, answer: str, faithfulness: float) -> bool:
        answer_lower = answer.lower()
        abstention_phrases = [
            "does not contain enough information",
            "context does not mention",
            "cannot be answered from the provided context",
            "not enough information to answer",
            "cannot answer this question",
            "information is not available in the context",
            "not found in the context",
            "missing from the context",
            "does not contain",
            "do not mention",
            "do not provide"
        ]
        has_abstention = any(phrase in answer_lower for phrase in abstention_phrases)
        return has_abstention
    
    def _extract_query_concepts(self, question: str) -> List[str]:
        question_lower = question.lower()
        words = re.findall(r'\b\w+\b', question_lower)
        concepts = [w for w in words if w not in self.NON_DOMAIN_TERMS and len(w) > 2]
        return concepts
    
    def _check_query_concepts_in_chunks(self, question: str, retrieved_chunks: List) -> float:
        if not retrieved_chunks:
            return 0.0
        
        concepts = self._extract_query_concepts(question)
        if not concepts:
            return 0.0
        
        context_text = " ".join([chunk.page_content.lower() for chunk in retrieved_chunks])
        matched = sum(1 for c in concepts if c in context_text)
        return matched / len(concepts) if concepts else 0.0
    
    def _rule_partial_answer_acceptable(self, answer: str, retrieved_chunks: List, faithfulness: float, recall: float, missing_concepts: List[str], corpus_concept_check: Optional[Dict]) -> Optional[Dict[str, Any]]:
        if faithfulness < 0.6:
            return None
        
        if not self._is_correct_abstention(answer, faithfulness):
            return None
        
        if not missing_concepts:
            return None
        
        concepts_missing_from_corpus = []
        if corpus_concept_check:
            concepts_missing_from_corpus = corpus_concept_check.get("concepts_missing_from_corpus", [])
        
        if not concepts_missing_from_corpus and missing_concepts:
            return None
        
        grounding_overlap = self._verify_claim_grounding(answer, retrieved_chunks)
        if grounding_overlap < 0.5:
            return None
        
        filtered_missing = self._filter_domain_concepts(concepts_missing_from_corpus) if concepts_missing_from_corpus else self._filter_domain_concepts(missing_concepts)
        if not filtered_missing:
            return None
        
        confidence = self._calculate_confidence(recall, grounding_overlap, 0.0)
        fix = "No action required. Answer is grounded but incomplete due to corpus limits."
        evidence = {
            "missing_concepts": filtered_missing[:3],
            "grounding_overlap": round(grounding_overlap, 2),
            "faithfulness_score": faithfulness,
            "abstention_detected": True,
            "confidence_formula": f"recall({recall:.2f})*0.4 + grounding({grounding_overlap:.2f})*0.4 + delta(0.00)*0.2"
        }
        user_explanation = f"Your answer is grounded and correct, but incomplete because the corpus doesn't contain information about: {', '.join(filtered_missing[:3])}. This is acceptable - the system correctly abstained from making unsupported claims."
        is_unfixable = True
        
        return {
            "rank": 2,
            "type": "Partial Answer (Acceptable)",
            "fix": fix,
            "user_explanation": user_explanation,
            "is_unfixable": is_unfixable,
            "evidence": evidence,
            "confidence": confidence
        }
    
    def _rule8_hallucination(self, faithfulness: float, unsupported_claims: List, config: Dict, answer: str, question: str = "") -> Optional[Dict[str, Any]]:
        if self._is_correct_abstention(answer, faithfulness):
            return None
        
        if self._has_uncertainty_language(answer):
            return None
        
        if faithfulness < 0.7 and unsupported_claims:
            temperature = config.get("temperature", 0.7)
            confidence = self._calculate_confidence(0.5, 0.3, 0.0)
            fix = f"Lower temperature from {temperature} or enforce extractive answering"
            evidence = {
                "unsupported_claims_count": len(unsupported_claims),
                "faithfulness_score": faithfulness,
                "confidence_formula": f"recall(0.50)*0.4 + grounding(0.30)*0.4 + delta(0.00)*0.2"
            }
            user_explanation, is_unfixable = self._get_user_explanation_and_unfixable("Generation Control", fix, evidence, question)
            
            return {
                "rank": 1,
                "type": "Generation Control",
                "fix": fix,
                "user_explanation": user_explanation,
                "is_unfixable": is_unfixable,
                "evidence": evidence,
                "confidence": confidence
            }
        return None
    
    def _rule9_cost_inefficiency(self, cost_optimization: Optional[Dict], retrieved_chunks: List, answer: str, evaluation_results: Dict, config: Dict, question: str = "") -> Optional[Dict[str, Any]]:
        if not cost_optimization:
            return None
        
        recall_val = evaluation_results.get("context_recall", {}).get("context_recall", 0.5)
        if recall_val < 0.6:
            return None
        
        triggers_fired = 0
        dominant_trigger = None
        evidence = {}
        
        unused_ratio = self._calculate_unused_chunks_ratio(retrieved_chunks, answer)
        if unused_ratio >= 0.4:
            triggers_fired += 1
            dominant_trigger = "unused_chunks"
            evidence["unused_chunks_ratio"] = unused_ratio
        
        wasted_cost = cost_optimization.get("wasted_cost", 0.0)
        total_cost = cost_optimization.get("total_cost", 0.0)
        total_tokens = cost_optimization.get("total_tokens", 0)
        wasted_tokens = cost_optimization.get("wasted_tokens", 0)
        
        used_tokens = total_tokens - wasted_tokens
        if used_tokens > 0 and total_cost > 0:
            cost_per_useful_token = total_cost / used_tokens
            if cost_per_useful_token > 0.0001:
                triggers_fired += 1
                if not dominant_trigger:
                    dominant_trigger = "cost_per_token"
                evidence["cost_per_useful_token"] = cost_per_useful_token
        
        sources_retrieved = len(set([c.metadata.get("source", "unknown") for c in retrieved_chunks if hasattr(c, "metadata") and c.metadata]))
        sources_used = self._count_used_sources(retrieved_chunks, answer)
        
        if sources_retrieved >= 5 and sources_used <= 1:
            triggers_fired += 1
            if not dominant_trigger:
                dominant_trigger = "metadata_overfetch"
            evidence["sources_retrieved"] = sources_retrieved
            evidence["sources_used"] = sources_used
        
        if triggers_fired >= 2 or dominant_trigger:
            fix = self._get_rule9_fix(dominant_trigger or "unused_chunks", config)
            evidence["wasted_cost_usd"] = wasted_cost
            
            recall_val = evaluation_results.get("context_recall", {}).get("context_recall", 0.5)
            grounding_overlap = 0.6
            counterfactual_delta = 0.05
            confidence = self._calculate_confidence(recall_val, grounding_overlap, counterfactual_delta)
            if triggers_fired >= 2:
                confidence = min(confidence + 0.1, 1.0)
            
            evidence["confidence_formula"] = f"recall({recall_val:.2f})*0.4 + grounding({grounding_overlap:.2f})*0.4 + delta({counterfactual_delta:.2f})*0.2"
            user_explanation, is_unfixable = self._get_user_explanation_and_unfixable("Cost Inefficiency", fix, evidence, question)
            
            return {
                "rank": 1,
                "type": "Cost Inefficiency",
                "fix": fix,
                "user_explanation": user_explanation,
                "is_unfixable": is_unfixable,
                "evidence": evidence,
                "confidence": confidence
            }
        
        return None
    
    def _rule10_systemic_drift(self, signals: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if len(self.query_history) >= 5:
            recent_failures = [q for q in self.query_history[-10:] if q.get("has_failure")]
            if len(recent_failures) >= 5:
                failure_types = [f.get("failure_type") for f in recent_failures]
                most_common = Counter(failure_types).most_common(1)
                if most_common and most_common[0][1] >= 3:
                    fix = "Apply global configuration update"
                    evidence = {
                        "failure_frequency": len(recent_failures) / 10,
                        "parameter_trigger_count": most_common[0][1]
                    }
                    question = signals.get("question", "")
                    user_explanation, is_unfixable = self._get_user_explanation_and_unfixable("Systemic Drift", fix, evidence, question)
                    
                    return {
                        "rank": 1,
                        "type": "System Configuration Drift",
                        "fix": fix,
                        "user_explanation": user_explanation,
                        "is_unfixable": is_unfixable,
                        "evidence": evidence,
                        "confidence": 0.80
                    }
        return None
    
    def _classify_outcome(self, evaluation_results: Optional[Dict], root_causes: List[Dict]) -> str:
        if not evaluation_results:
            return "FAILURE" # No eval = assumes something broke
            
        faithfulness_data = evaluation_results.get("faithfulness", {})
        faithfulness = faithfulness_data.get("faithfulness_factual", faithfulness_data.get("faithfulness", 1.0))
        relevance = evaluation_results.get("relevance", {}).get("relevance", 1.0)
        
        # 1. Verification Gate (Metrics)
        if faithfulness < 0.7 or relevance < 0.5:
            return "FAILURE"
            
        # 2. Risk Gate (Root Causes)
        # If metrics are good, but we found issues (Typo, Cost, etc.), it's Success with Risk
        if root_causes:
            return "SUCCESS_WITH_RISK"
            
        # 3. Clean Success
        return "SUCCESS"
    
    def _calculate_unused_chunks_ratio(self, retrieved_chunks: List, answer: str) -> float:
        if not retrieved_chunks:
            return 0.0
        
        used = 0
        answer_lower = answer.lower()
        
        for chunk in retrieved_chunks:
            content = chunk.page_content.lower()
            words = content.split()[:10]
            if any(word in answer_lower for word in words if len(word) > 4):
                used += 1
        
        return 1.0 - (used / len(retrieved_chunks))
    
    def _count_used_chunks(self, retrieved_chunks: List, answer: str) -> int:
        if not retrieved_chunks:
            return 0
        
        used = 0
        answer_lower = answer.lower()
        
        for chunk in retrieved_chunks:
            content = chunk.page_content.lower()
            words = content.split()[:10]
            if any(word in answer_lower for word in words if len(word) > 4):
                used += 1
        
        return used
    
    def _count_used_sources(self, retrieved_chunks: List, answer: str) -> int:
        used_sources = set()
        answer_lower = answer.lower()
        
        for chunk in retrieved_chunks:
            if hasattr(chunk, "metadata") and chunk.metadata:
                source = chunk.metadata.get("source", "")
                if source:
                    content = chunk.page_content.lower()
                    words = content.split()[:10]
                    if any(word in answer_lower for word in words if len(word) > 4):
                        used_sources.add(source)
        
        return len(used_sources)
    
    def _get_rule9_fix(self, trigger: str, config: Dict) -> str:
        if trigger == "unused_chunks":
            top_k = config.get("top_k", 3)
            return f"Reduce top_k from {top_k}"
        elif trigger == "marginal_utility":
            chunk_size = config.get("chunk_size", 500)
            return f"Reduce chunk_size from {chunk_size}"
        elif trigger == "cost_per_token":
            return "Compress context or rerank"
        elif trigger == "metadata_overfetch":
            return "Enable source-level filtering"
        elif trigger == "repeated_waste":
            return "Apply global default change"
        else:
            top_k = config.get("top_k", 3)
            return f"Reduce top_k from {top_k}"
    
    def _load_query_history(self):
        self.query_history = []
        if self.query_history_file.exists():
            try:
                with open(self.query_history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.query_history = data if isinstance(data, list) else []
            except (IOError, OSError, json.JSONDecodeError, ValueError) as e:
                self.query_history = []
        else:
            self.query_history = []
    
    def _save_query_history(self):
        try:
            self.query_history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.query_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.query_history, f, indent=2, ensure_ascii=False)
        except (IOError, OSError, json.JSONEncodeError):
            pass
    
    def _load_fix_history(self):
        self.fix_history = []
        if self.fix_history_file.exists():
            try:
                with open(self.fix_history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.fix_history = data if isinstance(data, list) else []
            except (IOError, OSError, json.JSONDecodeError, ValueError):
                self.fix_history = []
    
    def _save_fix_history(self):
        try:
            self.fix_history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.fix_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.fix_history, f, indent=2, ensure_ascii=False)
        except (IOError, OSError, json.JSONEncodeError):
            pass
    
    def _generate_fix_id(self, fix: str, rule_type: str) -> Optional[str]:
        if not fix:
            return None
        
        fix_lower = fix.lower()
        
        if "top_k" in fix_lower:
            match = re.search(r'top_k from (\d+) to (\d+)', fix_lower)
            if match:
                current = int(match.group(1))
                suggested = int(match.group(2))
                delta = suggested - current
                return f"retrieval.top_k:{delta:+d}"
            match = re.search(r'reduce top_k from (\d+)', fix_lower)
            if match:
                current = int(match.group(1))
                return f"retrieval.top_k:-1"
        
        if "temperature" in fix_lower:
            match = re.search(r'temperature from ([\d.]+)', fix_lower)
            if match:
                current = float(match.group(1))
                return f"generation.temperature:-{current:.1f}"
        
        if "chunk_size" in fix_lower:
            match = re.search(r'chunk_size from (\d+)', fix_lower)
            if match:
                current = int(match.group(1))
                return f"retrieval.chunk_size:-{current}"
        
        return None
    
    def _extract_config_params(self, config: Dict[str, Any], fix_id: Optional[str]) -> Dict[str, Any]:
        if not fix_id:
            return {}
        
        params = {}
        if "top_k" in fix_id:
            params["top_k"] = config.get("top_k")
        if "temperature" in fix_id:
            params["temperature"] = config.get("temperature")
        if "chunk_size" in fix_id:
            params["chunk_size"] = config.get("chunk_size")
        
        return params
    
    def _detect_active_fix(self, config: Dict[str, Any]) -> Optional[str]:
        for fix_record in reversed(self.fix_history):
            fix_id = fix_record.get("fix_id")
            if not fix_id:
                continue
            
            config_before = fix_record.get("config_before", {})
            
            if "top_k" in fix_id:
                current_top_k = config.get("top_k")
                before_top_k = config_before.get("top_k")
                if before_top_k and current_top_k:
                    match = re.search(r':([+-]?\d+)', fix_id)
                    if match:
                        expected_delta = int(match.group(1))
                        actual_delta = current_top_k - before_top_k
                        if actual_delta == expected_delta:
                            return fix_id
            
            if "temperature" in fix_id:
                current_temp = config.get("temperature")
                before_temp = config_before.get("temperature")
                if before_temp and current_temp:
                    match = re.search(r':-([\d.]+)', fix_id)
                    if match:
                        expected_delta = -float(match.group(1))
                        actual_delta = current_temp - before_temp
                        if abs(actual_delta - expected_delta) < 0.1:
                            return fix_id
            
            if "chunk_size" in fix_id:
                current_size = config.get("chunk_size")
                before_size = config_before.get("chunk_size")
                if before_size and current_size:
                    match = re.search(r':-(\d+)', fix_id)
                    if match:
                        expected_delta = -int(match.group(1))
                        actual_delta = current_size - before_size
                        if actual_delta == expected_delta:
                            return fix_id
        
        return None
    
    def get_report(self, last_n: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate system health report from query history.
        
        Args:
            last_n: Optional number of recent queries to analyze. If None, analyzes all queries.
        
        Returns:
            Dictionary containing:
                - system_verdict (str): Overall system health assessment
                - total_queries (int): Total queries analyzed
                - failed_queries (int): Number of failed queries
                - success_queries (int): Number of successful queries
                - success_with_risk (int): Number of successful queries with risks
                - failure_rate (float): Proportion of failed queries (0.0-1.0)
                - most_common_failure (dict): Most frequent failure type with count and percentage
                - most_common_risk (dict): Most frequent risk type with count
                - most_expensive_failure (dict): Failure type with highest cost
                - immediate_action (str): Recommended immediate action based on recent queries
                - strategic_action (str): Recommended strategic action based on all queries
                - total_cost_waste_usd (float): Total wasted cost in USD
                - total_cost_saved_usd (float): Estimated cost savings from successful queries
                - average_confidence (float): Average confidence score across queries
        """
        self._load_query_history()
        
        if last_n and last_n > 0:
            queries = self.query_history[-last_n:]
        else:
            queries = self.query_history.copy()
        
        if not queries:
            return {
                "total_queries": 0,
                "message": "No queries found"
            }
        
        failed_queries = []
        success_risky = []
        success_clean = []
        
        for q in queries:
            outcome = q.get("outcome")
            if not outcome:
                outcome = "FAILURE" if q.get("has_failure") else "SUCCESS"
            
            if outcome == "FAILURE":
                failed_queries.append(q)
            elif outcome == "SUCCESS_WITH_RISK":
                success_risky.append(q)
            else:
                success_clean.append(q)
        
        actionable_queries = failed_queries + success_risky
        
        root_cause_counter = Counter([q.get("root_cause") for q in failed_queries if q.get("root_cause")])
        most_common_failure = root_cause_counter.most_common(1)[0] if root_cause_counter else None
        most_common_failure_type = most_common_failure[0] if most_common_failure else None
        
        risk_counter = Counter([q.get("root_cause") for q in success_risky if q.get("root_cause")])
        most_common_risk = risk_counter.most_common(1)[0] if risk_counter else None
        most_common_risk_type = most_common_risk[0] if most_common_risk else None
        
        cost_by_failure = {}
        for q in actionable_queries:
            failure_type = q.get("root_cause")
            cost = q.get("cost_waste", 0.0)
            if failure_type:
                cost_by_failure[failure_type] = cost_by_failure.get(failure_type, 0.0) + cost
        
        most_expensive_failure = max(cost_by_failure.items(), key=lambda x: x[1]) if cost_by_failure else None
        
        total_history = len(self.query_history)
        if total_history < 10:
            immediate_window = 1
        elif total_history > 1000:
            immediate_window = 100
        else:
            immediate_window = max(1, int(total_history * 0.1))
        
        recent_queries = self.query_history[-immediate_window:] if total_history > 0 else []
        recent_failed = [q for q in recent_queries if q.get("outcome") == "FAILURE"]
        recent_risky = [q for q in recent_queries if q.get("outcome") == "SUCCESS_WITH_RISK"]
        
        def _is_old_fix_format(fix: str) -> bool:
            if not fix:
                return True
            return fix.startswith("Add documents containing:")
        
        if recent_failed and most_common_failure_type:
            recent_fixes = [q.get("fix") for q in recent_failed if q.get("fix") and q.get("root_cause") == most_common_failure_type and not _is_old_fix_format(q.get("fix"))]
            if recent_fixes:
                recent_fix_counter = Counter(recent_fixes)
                immediate_action = recent_fix_counter.most_common(1)[0][0]
            else:
                immediate_action = "Investigate failures"
        elif recent_risky and most_common_risk_type:
            recent_fixes = [q.get("fix") for q in recent_risky if q.get("fix") and q.get("root_cause") == most_common_risk_type and not _is_old_fix_format(q.get("fix"))]
            if recent_fixes:
                recent_fix_counter = Counter(recent_fixes)
                immediate_action = recent_fix_counter.most_common(1)[0][0]
            else:
                immediate_action = "Optimize risks"
        elif recent_failed:
            recent_fixes = [q.get("fix") for q in recent_failed if q.get("fix") and not _is_old_fix_format(q.get("fix"))]
            if recent_fixes:
                recent_fix_counter = Counter(recent_fixes)
                immediate_action = recent_fix_counter.most_common(1)[0][0]
            else:
                immediate_action = "Investigate failures"
        elif recent_risky:
            recent_fixes = [q.get("fix") for q in recent_risky if q.get("fix") and not _is_old_fix_format(q.get("fix"))]
            if recent_fixes:
                recent_fix_counter = Counter(recent_fixes)
                immediate_action = recent_fix_counter.most_common(1)[0][0]
            else:
                immediate_action = "Optimize risks"
        else:
            immediate_action = "No action required"
        
        if failed_queries and most_common_failure_type:
            fixes = [q.get("fix") for q in failed_queries if q.get("fix") and q.get("root_cause") == most_common_failure_type and not _is_old_fix_format(q.get("fix"))]
            if fixes:
                fix_counter = Counter(fixes)
                strategic_action = fix_counter.most_common(1)[0][0]
            else:
                strategic_action = "Investigate failures"
        elif success_risky and most_common_risk_type:
            fixes = [q.get("fix") for q in success_risky if q.get("fix") and q.get("root_cause") == most_common_risk_type and not _is_old_fix_format(q.get("fix"))]
            if fixes:
                fix_counter = Counter(fixes)
                strategic_action = fix_counter.most_common(1)[0][0]
            else:
                strategic_action = "Optimize risks"
        elif failed_queries:
            fixes = [q.get("fix") for q in failed_queries if q.get("fix") and not _is_old_fix_format(q.get("fix"))]
            if fixes:
                fix_counter = Counter(fixes)
                strategic_action = fix_counter.most_common(1)[0][0]
            else:
                strategic_action = "Investigate failures"
        elif success_risky:
            fixes = [q.get("fix") for q in success_risky if q.get("fix") and not _is_old_fix_format(q.get("fix"))]
            if fixes:
                fix_counter = Counter(fixes)
                strategic_action = fix_counter.most_common(1)[0][0]
            else:
                strategic_action = "Optimize risks"
        else:
            strategic_action = "System healthy"
        
        total_cost_waste = sum(q.get("cost_waste", 0.0) for q in queries)
        
        total_cost_all = sum(q.get("total_cost", 0.0) for q in queries if q.get("total_cost"))
        if total_cost_all == 0:
            for q in queries:
                if q.get("cost_waste", 0.0) > 0:
                    total_cost_all += q.get("cost_waste", 0.0) * 2
        
        total_cost_saved = 0.0
        if failed_queries:
            avg_waste_per_failed = total_cost_waste / len(failed_queries)
            if avg_waste_per_failed > 0:
                total_cost_saved = len(success_clean) * avg_waste_per_failed
            elif total_cost_all > 0:
                avg_cost_per_query = total_cost_all / len(queries)
                total_cost_saved = len(success_clean) * avg_cost_per_query * 0.3
        
        avg_confidence = sum(q.get("confidence", 0.0) for q in actionable_queries) / len(actionable_queries) if actionable_queries else 0.0
        
        failure_rate = len(failed_queries) / len(queries) if queries else 0.0
        
        severity_scores = []
        for q in failed_queries:
            confidence = q.get("confidence", 0.0)
            cost = max(q.get("cost_waste", 0.0), 0.0001)
            recurrence = 1.0
            
            failure_type = q.get("root_cause")
            if failure_type:
                same_type_count = sum(1 for fq in failed_queries if fq.get("root_cause") == failure_type)
                recurrence = min(same_type_count / len(failed_queries), 1.0) if failed_queries else 1.0
            
            severity = confidence * cost * (1.0 + recurrence)
            severity_scores.append(severity)
        
        max_severity = max(severity_scores) if severity_scores else 0.0
        avg_severity = sum(severity_scores) / len(severity_scores) if severity_scores else 0.0
        severity_threshold = 0.01
        
        recent_failed_count = len(recent_failed)
        
        most_common_failure_type = most_common_failure[0] if most_common_failure else None
        most_common_failure_pct = (most_common_failure[1] / len(failed_queries)) * 100 if most_common_failure and failed_queries else 0
        
        if failure_rate >= 0.4:
            if most_common_failure_type == "Corpus Coverage" and most_common_failure_pct >= 50:
                system_verdict = "Domain-Bounded System. Corpus coverage limits answerability."
            elif most_common_failure_type == "Corpus Coverage" and most_common_failure_pct >= 30:
                system_verdict = "Healthy but Corpus-Limited. Expand corpus to improve coverage."
            elif most_common_failure_type == "Retrieval Configuration" and most_common_failure_pct >= 50:
                system_verdict = "Retrieval-Constrained System. Adjust retrieval parameters."
            elif most_common_failure_type == "Generation Control" and most_common_failure_pct >= 50:
                system_verdict = "Generation-Constrained System. Adjust generation parameters."
            elif most_common_failure_type == "User Query" and most_common_failure_pct >= 50:
                system_verdict = "Query Quality Issues. Improve query preprocessing."
            elif recent_failed_count >= 2:
                system_verdict = "Immediate action required."
            else:
                system_verdict = "System needs attention. Review failure patterns."
        elif failure_rate >= 0.2:
            if most_common_failure_type == "Corpus Coverage" and most_common_failure_pct >= 40:
                system_verdict = "Healthy but Corpus-Limited. Consider expanding corpus."
            elif most_common_failure_type == "Retrieval Configuration":
                system_verdict = "Retrieval Optimization Needed. Fine-tune retrieval settings."
            elif most_common_failure_type == "Generation Control":
                system_verdict = "Generation Optimization Needed. Adjust generation parameters."
            elif recent_failed_count >= 2:
                system_verdict = "System stable with known risks."
            else:
                system_verdict = "System stable. Monitor failure patterns."
        elif failure_rate > 0:
            if most_common_failure_type == "Corpus Coverage":
                system_verdict = "Healthy but Corpus-Limited. Minor gaps detected."
            elif len(success_risky) > len(failed_queries):
                system_verdict = "System healthy with optimization opportunities."
            else:
                system_verdict = "System healthy. Minor issues detected."
        elif len(success_risky) > 0:
            if most_common_risk and most_common_risk[0] == "Corpus Coverage":
                system_verdict = "System healthy. Corpus expansion recommended."
            else:
                system_verdict = "System healthy. Minor risks detected."
        else:
            system_verdict = "System healthy."
        
        report = {
            "system_verdict": system_verdict,
            "total_queries": len(queries),
            "failed_queries": len(failed_queries),
            "success_queries": len(success_clean),
            "success_with_risk": len(success_risky),
            "failure_rate": round(failure_rate, 2),
            "most_common_failure": {
                "type": most_common_failure[0],
                "count": most_common_failure[1],
                "percentage": round((most_common_failure[1] / len(failed_queries)) * 100, 1) if failed_queries else 0
            } if most_common_failure else None,
            "most_common_risk": {
                 "type": most_common_risk[0],
                 "count": most_common_risk[1]
            } if most_common_risk else None,
            "most_expensive_failure": {
                "type": most_expensive_failure[0],
                "total_cost_usd": round(most_expensive_failure[1], 6)
            } if most_expensive_failure else None,
            "immediate_action": immediate_action,
            "strategic_action": strategic_action,
            "total_cost_waste_usd": round(total_cost_waste, 6),
            "total_cost_saved_usd": round(total_cost_saved, 6),
            "average_confidence": round(avg_confidence, 2)
        }
        
        return report
    
    def _finalize_attribution(self, root_causes: List[Dict[str, Any]], query_id: str, question: str, cost_optimization: Optional[Dict] = None, evaluation_results: Optional[Dict] = None) -> Dict[str, Any]:
        if not root_causes:
            return {
                "query_id": query_id,
                "question": question,
                "root_causes": []
            }
        
        for idx, cause in enumerate(root_causes, 1):
            cause["rank"] = idx
        
        if len(root_causes) == 1:
            final_causes = root_causes
        else:
            conf1 = root_causes[0].get("confidence", 0.0)
            conf2 = root_causes[1].get("confidence", 0.0) if len(root_causes) > 1 else 0.0
            
            conf_gap = conf1 - conf2
            if conf_gap < 0.25:
                final_causes = root_causes[:2]
            else:
                final_causes = root_causes[:1]
        
        primary_failure = final_causes[0] if final_causes else None
        secondary_risk = final_causes[1] if len(final_causes) > 1 else None
        
        result = {
            "query_id": query_id,
            "question": question,
            "root_causes": final_causes,
            "primary_failure": primary_failure,
            "secondary_risk": secondary_risk,
            "decision_reason": "highest confidence + strongest evidence"
        }
        
        return result
    
    def validate_fix(self, fix_id: Optional[str] = None, before_query_ids: Optional[List[str]] = None, after_query_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate the effectiveness of an applied fix by comparing metrics before and after.
        
        Args:
            fix_id: Optional fix identifier. If provided, automatically detects before/after queries
                    based on fix application timestamp.
            before_query_ids: Optional list of query IDs before fix was applied.
            after_query_ids: Optional list of query IDs after fix was applied.
        
        Returns:
            Dictionary containing:
                - verdict (str): "Fix effective", "Fix ineffective", "NO_SIGNIFICANT_CHANGE",
                                "FIX_NOT_FOUND", "FIX_NOT_APPLIED", "INSUFFICIENT_DATA", or "INVALID_ARGUMENTS"
                - fix_applied (str): Description of the applied fix
                - failure_rate_change (str): Change in failure rate as percentage (e.g., "-5.0%")
                - retrieval_recall_change (str): Change in average retrieval recall
                - cost_change_usd (str): Change in average cost per query in USD
                - before_count (int, optional): Number of queries before fix (if insufficient data)
                - after_count (int, optional): Number of queries after fix (if insufficient data)
                - message (str, optional): Additional message (if error)
        """
        if before_query_ids is not None and after_query_ids is not None:
            return self.validate_fix_by_queries(before_query_ids, after_query_ids)
        
        if not fix_id:
            return {"verdict": "INVALID_PARAMETERS", "message": "Either fix_id or before_query_ids/after_query_ids required"}
        
        fix_records = [f for f in self.fix_history if f.get("fix_id") == fix_id]
        if not fix_records:
            return {"verdict": "FIX_NOT_FOUND"}
        
        fix_record = fix_records[0]
        applied_at = fix_record.get("applied_at")
        if not applied_at:
            return {"verdict": "FIX_NOT_APPLIED"}
        
        before_queries = [q for q in self.query_history if q.get("timestamp") < applied_at]
        after_queries = [q for q in self.query_history if q.get("timestamp") >= applied_at and q.get("active_fix_id") == fix_id]
        
        if len(before_queries) < 10 or len(after_queries) < 10:
            return {"verdict": "INSUFFICIENT_DATA", "before_count": len(before_queries), "after_count": len(after_queries)}
        
        before_success = sum(1 for q in before_queries if q.get("outcome") in ["SUCCESS", "SUCCESS_WITH_RISK"])
        before_failure = sum(1 for q in before_queries if q.get("outcome") == "FAILURE")
        before_total_cost = sum(q.get("total_cost", 0.0) for q in before_queries)
        
        after_success = sum(1 for q in after_queries if q.get("outcome") in ["SUCCESS", "SUCCESS_WITH_RISK"])
        after_failure = sum(1 for q in after_queries if q.get("outcome") == "FAILURE")
        after_total_cost = sum(q.get("total_cost", 0.0) for q in after_queries)
        
        before_success_rate = before_success / len(before_queries) if before_queries else 0.0
        after_success_rate = after_success / len(after_queries) if after_queries else 0.0
        before_failure_rate = before_failure / len(before_queries) if before_queries else 0.0
        after_failure_rate = after_failure / len(after_queries) if after_queries else 0.0
        before_avg_cost = before_total_cost / len(before_queries) if before_queries else 0.0
        after_avg_cost = after_total_cost / len(after_queries) if after_queries else 0.0
        
        success_improvement = after_success_rate - before_success_rate
        failure_reduction = before_failure_rate - after_failure_rate
        cost_change = after_avg_cost - before_avg_cost
        
        threshold = 0.05
        if success_improvement > threshold or failure_reduction > threshold:
            verdict = "IMPROVED"
        elif success_improvement < -threshold or failure_reduction < -threshold:
            verdict = "REGRESSED"
        else:
            verdict = "NO_SIGNIFICANT_CHANGE"
        
        return {
            "fix_id": fix_id,
            "verdict": verdict,
            "before": {
                "success_rate": before_success_rate,
                "failure_rate": before_failure_rate,
                "average_cost": before_avg_cost,
                "sample_size": len(before_queries)
            },
            "after": {
                "success_rate": after_success_rate,
                "failure_rate": after_failure_rate,
                "average_cost": after_avg_cost,
                "sample_size": len(after_queries)
            }
        }
    
    def apply_fix(self, fix_id: str) -> bool:
        """
        Mark a fix as applied in the fix history.
        
        Args:
            fix_id: Fix identifier to mark as applied
        
        Returns:
            True if fix was found and marked as applied, False otherwise
        """
        for fix_record in self.fix_history:
            if fix_record.get("fix_id") == fix_id and not fix_record.get("applied_at"):
                fix_record["applied_at"] = datetime.now().isoformat()
                self._save_fix_history()
                return True
        return False
    
    def validate_fix_by_queries(self, before_query_ids: List[str], after_query_ids: List[str]) -> Dict[str, Any]:
        before_queries = [q for q in self.query_history if q.get("query_id") in before_query_ids]
        after_queries = [q for q in self.query_history if q.get("query_id") in after_query_ids]
        
        if not before_queries or not after_queries:
            return {"verdict": "INSUFFICIENT_DATA", "message": "Query IDs not found in history"}
        
        before_failures = sum(1 for q in before_queries if q.get("outcome") == "FAILURE")
        after_failures = sum(1 for q in after_queries if q.get("outcome") == "FAILURE")
        
        before_failure_rate = before_failures / len(before_queries) if before_queries else 0.0
        after_failure_rate = after_failures / len(after_queries) if after_queries else 0.0
        failure_rate_change = after_failure_rate - before_failure_rate
        failure_rate_change_pct = failure_rate_change * 100
        
        before_total_cost = sum(q.get("total_cost", 0.0) for q in before_queries)
        after_total_cost = sum(q.get("total_cost", 0.0) for q in after_queries)
        before_avg_cost = before_total_cost / len(before_queries) if before_queries else 0.0
        after_avg_cost = after_total_cost / len(after_queries) if after_queries else 0.0
        cost_change = after_avg_cost - before_avg_cost
        
        active_fix_ids = [q.get("active_fix_id") for q in after_queries if q.get("active_fix_id")]
        fix_applied = None
        if active_fix_ids:
            most_common_fix_id = max(set(active_fix_ids), key=active_fix_ids.count)
            fix_record = next((f for f in self.fix_history if f.get("fix_id") == most_common_fix_id), None)
            if fix_record:
                fix_applied = fix_record.get("fix", "Unknown fix")
        
        trace_log_dir = self.query_history_file.parent
        before_recall_sum = 0.0
        before_recall_count = 0
        after_recall_sum = 0.0
        after_recall_count = 0
        
        for query_id in before_query_ids:
            trace_file = trace_log_dir / f"{query_id}.json"
            if trace_file.exists():
                try:
                    with open(trace_file, 'r', encoding='utf-8') as f:
                        trace_data = json.load(f)
                        eval_data = trace_data.get("evaluation", {})
                        if not eval_data and "trace" in trace_data:
                            eval_data = trace_data.get("trace", {}).get("evaluation", {})
                        recall = eval_data.get("context_recall", {}).get("context_recall", 0.0)
                        if recall > 0:
                            before_recall_sum += recall
                            before_recall_count += 1
                except:
                    pass
        
        for query_id in after_query_ids:
            trace_file = trace_log_dir / f"{query_id}.json"
            if trace_file.exists():
                try:
                    with open(trace_file, 'r', encoding='utf-8') as f:
                        trace_data = json.load(f)
                        eval_data = trace_data.get("evaluation", {})
                        if not eval_data and "trace" in trace_data:
                            eval_data = trace_data.get("trace", {}).get("evaluation", {})
                        recall = eval_data.get("context_recall", {}).get("context_recall", 0.0)
                        if recall > 0:
                            after_recall_sum += recall
                            after_recall_count += 1
                except:
                    pass
        
        before_avg_recall = before_recall_sum / before_recall_count if before_recall_count > 0 else 0.0
        after_avg_recall = after_recall_sum / after_recall_count if after_recall_count > 0 else 0.0
        retrieval_recall_change = after_avg_recall - before_avg_recall
        
        if failure_rate_change < -0.05 or (before_recall_count > 0 and after_recall_count > 0 and retrieval_recall_change > 0.05):
            verdict = "Fix effective"
        elif failure_rate_change > 0.05 or (before_recall_count > 0 and after_recall_count > 0 and retrieval_recall_change < -0.05):
            verdict = "Fix ineffective"
        else:
            verdict = "No significant change"
        
        result = {
            "fix_applied": fix_applied or "Unknown",
            "failure_rate_change": f"{failure_rate_change_pct:+.0f}%",
            "cost_change_usd": f"{cost_change:+.6f}",
            "verdict": verdict
        }
        
        if before_recall_count > 0 and after_recall_count > 0:
            result["retrieval_recall_change"] = f"{retrieval_recall_change:+.2f}"
        
        return result
    
    def get_public_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a simplified, stable output format for public/production API.
        
        This method provides a backward-compatible, stable schema that includes only
        essential fields for external consumption.
        
        Args:
            result: Full analysis result from analyze() method
        
        Returns:
            Dictionary containing:
                - query_id (str): Query identifier
                - outcome (str): "SUCCESS", "SUCCESS_WITH_RISK", or "FAILURE"
                - primary_failure (str, optional): Primary failure type
                - recommended_fix (str, optional): Recommended fix for the primary failure
                - is_unfixable (bool): Whether the fix requires data/corpus changes
                - confidence (float): Confidence score (0.0-1.0)
                - explanation (str): User-friendly explanation
                - diagnostic_maturity (str): "experimental", "stable", or "high-confidence"
        """
        root_causes = result.get("root_causes", [])
        primary = root_causes[0] if root_causes else None
        
        if primary:
            confidence = primary.get("confidence", 0.0)
            if confidence >= 0.8:
                maturity = "high-confidence"
            elif confidence >= 0.5:
                maturity = "stable"
            else:
                maturity = "experimental"
        else:
            maturity = "stable"
        
        return {
            "query_id": result.get("query_id"),
            "outcome": result.get("outcome", "UNKNOWN"),
            "primary_failure": primary.get("type") if primary else None,
            "recommended_fix": primary.get("fix") if primary else None,
            "is_unfixable": primary.get("is_unfixable", False) if primary else False,
            "confidence": primary.get("confidence", 0.0) if primary else 0.0,
            "explanation": primary.get("user_explanation", "") if primary else "",
            "diagnostic_maturity": maturity
        }
