from typing import Dict, Any, List, Callable, Optional
from copy import deepcopy
from langchain_core.documents import Document


class Phase8Recommender:
    """
    Phase 8 - Fix Recommendation
    Generate controlled candidates, score them, and pick the best fix.
    Supports Retrieval, Generation, and Prompt failures.
    """

    RETRIEVAL_BLOCK_THRESHOLD = 0.45

    def __init__(self, retriever_getter: Callable, evaluator, generator_getter: Optional[Callable] = None):
        self.retriever_getter = retriever_getter
        self.evaluator = evaluator
        self.generator_getter = generator_getter

    def _score_retrieval_candidate(self, question: str, candidate: Dict, baseline_recall: float, baseline_missing: List[str], baseline_chunks: List[Document]) -> Optional[Dict]:
        """Score a retrieval candidate fix."""
        param = candidate["param"]
        new_value = candidate["target"]
        retriever = self.retriever_getter()
        if not retriever:
            return None
        
        if param == "top_k":
            chunks = retriever.retrieve(question, top_k=new_value)
        else:
            return None
        
        recall_eval = self.evaluator.evaluate_context_recall(question, chunks)
        recall = recall_eval["context_recall"]
        missing = recall_eval.get("missing_concepts", [])
        delta = round(recall - baseline_recall, 2)
        resolved = [c for c in baseline_missing if c not in missing]
        
        return {
            "param": param,
            "current": candidate["current"],
            "recommended": new_value,
            "recall": round(recall, 2),
            "delta_recall": delta,
            "missing_concepts": missing,
            "missing_concepts_resolved": resolved,
            "chunks": chunks
        }

    def _score_generation_candidate(self, question: str, candidate: Dict, baseline_faithfulness: float, baseline_unsupported: List, baseline_chunks: List[Document]) -> Optional[Dict]:
        """Score a generation candidate fix."""
        param = candidate["param"]
        generator = self.generator_getter() if self.generator_getter else None
        if not generator:
            return None
        
        original_temp = generator.temperature
        original_system = generator.system_prompt
        
        try:
            if param == "temperature":
                generator.update_temperature(candidate["target"])
                answer, _ = generator.generate(question, baseline_chunks)
                generator.update_temperature(original_temp)
            elif param == "system_prompt":
                generator.update_system_prompt(candidate["target"])
                answer, _ = generator.generate(question, baseline_chunks)
                generator.update_system_prompt(original_system)
            else:
                return None
            
            faith_eval = self.evaluator.evaluate_faithfulness(
                answer,
                baseline_chunks,
                question=question
            )
            faithfulness = faith_eval["faithfulness"]
            unsupported = faith_eval.get("unsupported_factual_claims", faith_eval.get("unsupported_claims", []))
            delta = round(faithfulness - baseline_faithfulness, 2)
            
            result = {
                "param": param,
                "current": candidate["current"],
                "recommended": candidate["target"],
                "faithfulness": round(faithfulness, 2),
                "delta_faithfulness": delta,
                "unsupported_claims": len(unsupported),
                "answer": answer
            }
            
            return result
        except Exception as e:
            if param == "temperature":
                try:
                    generator.update_temperature(original_temp)
                except:
                    pass
            elif param == "system_prompt":
                try:
                    generator.update_system_prompt(original_system)
                except:
                    pass
            return None

    def _score_prompt_candidate(self, question: str, candidate: Dict, baseline_relevance: float, baseline_chunks: List[Document]) -> Optional[Dict]:
        """Score a prompt candidate fix."""
        param = candidate["param"]
        generator = self.generator_getter() if self.generator_getter else None
        if not generator:
            return None
        
        original_system = generator.system_prompt
        
        try:
            if param == "system_prompt":
                generator.update_system_prompt(candidate["target"])
                answer, _ = generator.generate(question, baseline_chunks)
                generator.update_system_prompt(original_system)
            elif param == "user_prompt":
                custom_prompt = candidate["target"]
                answer, _ = generator.generate(question, baseline_chunks, custom_prompt=custom_prompt)
            else:
                return None
            
            relevance_eval = self.evaluator.evaluate_relevance(question, answer)
            relevance = relevance_eval["relevance"]
            delta = round(relevance - baseline_relevance, 2)
            
            recommended_display = candidate["target"]
            if isinstance(candidate["target"], str) and len(candidate["target"]) > 50:
                recommended_display = candidate["target"][:50] + "..."
            
            return {
                "param": param,
                "current": candidate.get("current", "default"),
                "recommended": recommended_display,
                "relevance": round(relevance, 2),
                "delta_relevance": delta,
                "answer": answer
            }
        except Exception as e:
            if param == "system_prompt":
                try:
                    generator.update_system_prompt(original_system)
                except:
                    pass
            return None

    def _generate_retrieval_candidates(self, config: Dict) -> List[Dict]:
        """Generate retrieval fix candidates."""
        top_k = config.get("top_k", 5)
        candidates = [
            {"param": "top_k", "current": top_k, "target": 8},
            {"param": "top_k", "current": top_k, "target": 12},
        ]
        return candidates

    def _generate_generation_candidates(self, config: Dict, baseline_chunks: List[Document]) -> List[Dict]:
        """Generate generation fix candidates."""
        temperature = config.get("temperature", 0.7)
        generator = self.generator_getter() if self.generator_getter else None
        current_system = generator.system_prompt if generator else "default"
        
        grounded_system = (
            "You are a precise assistant. Answer ONLY using information explicitly present in the provided context. "
            "Do not make up, infer, or add any information not in the context. If the context doesn't contain enough "
            "information to answer the question completely, state what information is missing."
        )
        
        candidates = [
            {"param": "temperature", "current": temperature, "target": 0.3},
            {"param": "temperature", "current": temperature, "target": 0.1},
            {"param": "system_prompt", "current": current_system, "target": grounded_system},
        ]
        return candidates

    def _generate_prompt_candidates(self, question: str, config: Dict, baseline_chunks: List[Document]) -> List[Dict]:
        """Generate prompt fix candidates."""
        generator = self.generator_getter() if self.generator_getter else None
        current_system = generator.system_prompt if generator else "default"
        
        format_system = (
            "You are a precise assistant. Answer the question directly and completely. "
            "Follow any specific format requirements in the question (lists, numbered items, structured data). "
            "Be explicit and detailed. Use only information from the provided context."
        )
        
        candidates = [
            {"param": "system_prompt", "current": current_system, "target": format_system},
            {
                "param": "user_prompt",
                "current": "default",
                "target": (
                    "Context:\n{context}\n\nQuestion: {question}\n\n"
                    "Instructions: Answer the question directly and completely. If the question asks for a specific format "
                    "(like lists, numbered items, or structured data), follow that format exactly. Be explicit and detailed.\n\nAnswer:"
                )
            },
        ]
        return candidates

    def recommend(self, question: str, baseline_eval: Dict, config: Dict, failure_attribution: Optional[Dict] = None, failure_detection: Optional[Dict] = None, baseline_chunks: Optional[List[Document]] = None, conflict_resolution: Optional[Dict] = None) -> Dict:
        """Recommend a fix based on the failure type. Uses Phase 7 attribution if available, otherwise Phase 4 detection."""
        # Prefer Phase 7 final attribution over Phase 4 initial hypothesis
        override_reason = None

        if failure_attribution and "primary_failure" in failure_attribution:
            component = failure_attribution["primary_failure"]
        elif failure_detection:
            component = failure_detection.get("failure_hypothesis", {}).get("primary", {}).get("component", "Unknown")
        else:
            return {"message": "No failure detection or attribution provided to Phase 8"}
        
        recall = baseline_eval.get("context_recall", {}).get("context_recall", 0.0)
        missing = baseline_eval.get("context_recall", {}).get("missing_concepts", [])
        faithfulness = baseline_eval.get("faithfulness", {}).get("faithfulness", 1.0)
        
        # Check if concepts are missing from corpus (not fixable by retrieval)
        concepts_missing_from_corpus = []
        if conflict_resolution:
            concepts_missing_from_corpus = conflict_resolution.get("concepts_missing_from_corpus", [])
            
        # Filter format keywords - don't ask user to add documents about "json" or "chart"
        format_keywords = {"json", "xml", "csv", "html", "yaml", "list", "table", "chart", "graph", "format", "style", "concept"}
        concepts_missing_from_corpus = [c for c in concepts_missing_from_corpus if c.lower() not in format_keywords]
        
        # Only consider retrieval blocked if concepts exist in corpus
        retrieval_blocked = (
            recall < self.RETRIEVAL_BLOCK_THRESHOLD 
            and len(missing) > 0 
            and len(concepts_missing_from_corpus) == 0  # Concepts must exist in corpus
        )

        # Issue 3: Handle ImprovementOpportunity by mapping to a physical component for advice
        if component == "ImprovementOpportunity":
            # Pick component with lowest metric
            recall = baseline_eval.get("context_recall", {}).get("context_recall", 1.0)
            faithfulness = baseline_eval.get("faithfulness", {}).get("faithfulness", 1.0)
            relevance = baseline_eval.get("relevance", {}).get("relevance", 1.0)
            
            # Find the component with the largest 'headroom' (distance from 1.0)
            headroom = {
                "Retrieval": 1.0 - recall,
                "Generation": 1.0 - faithfulness,
                "Prompt": 1.0 - relevance
            }
            component = max(headroom, key=headroom.get)
            is_advisory = True
        else:
            is_advisory = False

        # If concepts are missing from corpus, don't recommend retrieval fixes
        if len(concepts_missing_from_corpus) > 0 and component == "Retrieval":
            return {
                "recommended_fix": {
                    "component": "QueryDesign",
                    "parameter": "corpus_coverage",
                    "current": "insufficient",
                    "recommended": f"Add documents covering concepts: {', '.join(concepts_missing_from_corpus[:5])}",
                    "is_advisory": False
                },
                "justification": {
                    "reason": (
                        f"Concepts not present in corpus: {', '.join(concepts_missing_from_corpus[:3])}. "
                        "No amount of retrieval improvements (top_k, chunking, etc.) can retrieve concepts that don't exist. "
                        "Add relevant documents to the corpus instead."
                    ),
                    "missing_concepts_from_corpus": concepts_missing_from_corpus,
                    "type": "Blocker"
                }
            }
        
        if component == "Answerability":
            return {
                "recommended_fix": {
                    "component": "QueryDesign",
                    "parameter": "question_scope",
                    "current": "unspecified",
                    "recommended": "Rephrase query or add missing corpus coverage",
                    "is_advisory": False
                },
                "justification": {
                    "reason": "Phase A determined the query is not answerable with the current corpus.",
                    "missing_concepts": missing,
                    "type": "Blocker"
                }
            }

        if component in ("Generation", "Prompt") and retrieval_blocked:
            override_reason = (
                f"Causal precedence: context recall={recall:.2f} with {len(missing)} missing concepts. "
                "Retrieval must be fixed before touching later stages."
            )
            component = "Retrieval"

        if component == "Prompt":
            prompt_preconditions = recall >= 0.7 and len(missing) == 0
            if not prompt_preconditions:
                override_reason = (
                    "Prompt fixes require recall ≥ 0.7 and no missing concepts. "
                    "Routing suggestion to Retrieval instead."
                )
                component = "Retrieval"
            elif faithfulness >= 0.7:
                override_reason = (
                    "Faithfulness is not degraded enough to justify prompt changes. "
                    "Treating this as a Generation grounding issue."
                )
                component = "Generation"
        
        if component == "Retrieval":
            baseline_recall = baseline_eval["context_recall"]["context_recall"]
            baseline_missing = baseline_eval["context_recall"].get("missing_concepts", [])
            candidates = self._generate_retrieval_candidates(config)
            results = []
            for candidate in candidates:
                score = self._score_retrieval_candidate(question, candidate, baseline_recall, baseline_missing, baseline_chunks or [])
                if score:
                    results.append(score)
            
            if not results:
                return {"message": "No retrieval candidates executed."}
            
            best = max(
                results,
                key=lambda r: (
                    len(r["missing_concepts_resolved"]) > 0,
                    r["delta_recall"],
                    -abs(r["recommended"] - r["current"]) if isinstance(r["recommended"], (int, float)) else 0
                )
            )
            
            response = {
                "recommended_fix": {
                    "component": "Retriever",
                    "parameter": best["param"],
                    "current": best["current"],
                    "recommended": best["recommended"],
                    "is_advisory": is_advisory
                },
                "justification": {
                    "delta_recall": f"{best['delta_recall']:+.2f}",
                    "missing_concepts_resolved": best["missing_concepts_resolved"],
                    "risk_level": "low" if len(best["missing_concepts"]) == 0 else "medium",
                    "type": "Advisory" if is_advisory else "Critical"
                },
                "experiment_table": results
            }
            if override_reason:
                response["causal_precedence_note"] = override_reason
            return response
        
        elif component == "Generation":
            baseline_faithfulness = baseline_eval["faithfulness"]["faithfulness"]
            baseline_unsupported = baseline_eval["faithfulness"].get(
                "unsupported_factual_claims",
                baseline_eval["faithfulness"].get("unsupported_claims", [])
            )
            candidates = self._generate_generation_candidates(config, baseline_chunks or [])
            results = []
            for candidate in candidates:
                score = self._score_generation_candidate(question, candidate, baseline_faithfulness, baseline_unsupported, baseline_chunks or [])
                if score:
                    results.append(score)
            
            if not results:
                return {"message": "No generation candidates executed."}
            
            best = max(
                results,
                key=lambda r: (
                    r["delta_faithfulness"],
                    r["faithfulness"],
                    -abs(r["recommended"] - r["current"]) if isinstance(r["current"], (int, float)) and isinstance(r["recommended"], (int, float)) else 0
                )
            )
            
            response = {
                "recommended_fix": {
                    "component": "Generator",
                    "parameter": best["param"],
                    "current": best["current"],
                    "recommended": best["recommended"],
                    "is_advisory": is_advisory
                },
                "justification": {
                    "delta_faithfulness": f"{best['delta_faithfulness']:+.2f}",
                    "unsupported_claims_after": best["unsupported_claims"],
                    "risk_level": "low" if best["delta_faithfulness"] > 0 else "medium",
                    "type": "Advisory" if is_advisory else "Critical"
                },
                "experiment_table": results
            }
            if override_reason:
                response["causal_precedence_note"] = override_reason
            return response
        
        elif component == "Prompt":
            baseline_relevance = baseline_eval["relevance"]["relevance"]
            candidates = self._generate_prompt_candidates(question, config, baseline_chunks or [])
            results = []
            for candidate in candidates:
                score = self._score_prompt_candidate(question, candidate, baseline_relevance, baseline_chunks or [])
                if score:
                    results.append(score)
            
            if not results:
                return {"message": "No prompt candidates executed."}
            
            best = max(
                results,
                key=lambda r: (
                    r["delta_relevance"],
                    r["relevance"],
                    0
                )
            )
            
            response = {
                "recommended_fix": {
                    "component": "Prompt",
                    "parameter": best["param"],
                    "current": best["current"],
                    "recommended": best["recommended"],
                    "is_advisory": is_advisory
                },
                "justification": {
                    "delta_relevance": f"{best['delta_relevance']:+.2f}",
                    "risk_level": "low" if best["delta_relevance"] > 0 else "medium",
                    "type": "Advisory" if is_advisory else "Critical"
                },
                "experiment_table": results
            }
            if override_reason:
                response["causal_precedence_note"] = override_reason
            return response
        
        elif component == "User Query":
            return {
                "message": f"Fix typo in query: {conflict_resolution.get('rationale')}",
                "recommended_fix": {
                    "component": "User Query",
                    "parameter": "spelling",
                    "current": "incorrect",
                    "recommended": "correct",
                    "is_advisory": False
                },
                "justification": {
                    "delta_faithfulness": "+0.00",
                    "delta_recall": "+1.00",
                    "risk_level": "low",
                    "type": "Critical"
                },
                "experiment_table": []
            }
        
        else:
            return {
                "message": f"Phase 8 does not support fixes for component: {component}"
            }
