"""
Phase C: Counterfactual Fix Generator
Determines the minimal change that would flip failure into success.
This is diagnostic, not speculative.
"""

from typing import Dict, Any, List, Optional


class CounterfactualFixGenerator:
    """
    Generates counterfactual fixes - minimal changes that would prevent failure.
    
    This is NOT auto-fixing. This is diagnostic evidence showing:
    "If you had done X instead of Y, the failure would not have occurred."
    """
    
    def __init__(self):
        """Initialize the generator."""
        pass
    
    def _generate_retrieval_counterfactual(
        self,
        evaluation_results: Dict[str, Any],
        current_top_k: int,
        current_chunk_size: int
    ) -> Dict[str, Any]:
        """Generate counterfactual for retrieval failures."""
        
        recall = evaluation_results.get("context_recall", {}).get("context_recall", 0.0)
        missing_concepts = evaluation_results.get("context_recall", {}).get("missing_concepts", [])
        
        # Calculate expected improvement
        recall_gap = 1.0 - recall
        
        # Heuristic: Each 2 additional chunks improves recall by ~0.1
        needed_improvement = max(0.6 - recall, 0)  # Target 0.6 minimum
        additional_chunks = int(needed_improvement / 0.1) * 2
        
        # Ensure at least 2-3 additional chunks when recall is below 0.7
        if recall < 0.7 and additional_chunks == 0:
            additional_chunks = 2  # Minimum meaningful increase
        
        recommended_top_k = min(current_top_k + additional_chunks, 15)  # Cap at 15
        
        # Calculate expected improvement based on chunks being added (heuristic: 2 chunks ≈ 0.1 recall)
        expected_recall_improvement = min((additional_chunks / 2) * 0.1, recall_gap)
        
        return {
            "type": "Retrieval",
            "change": "Increase top_k",
            "current_value": current_top_k,
            "recommended_value": recommended_top_k,
            "expected_effect": f"+{expected_recall_improvement:.2f} context recall",
            "rationale": (
                f"Current recall={recall:.2f}. Missing concepts: {', '.join(missing_concepts[:3])}. "
                f"Increasing top_k from {current_top_k} to {recommended_top_k} would likely "
                f"retrieve chunks containing these concepts."
            ),
            "confidence": 0.75
        }
    
    def _generate_generation_counterfactual(
        self,
        evaluation_results: Dict[str, Any],
        current_temperature: float
    ) -> Dict[str, Any]:
        """Generate counterfactual for generation failures."""
        
        faithfulness = evaluation_results.get("faithfulness", {}).get("faithfulness", 0.0)
        unsupported_claims = evaluation_results.get("faithfulness", {}).get("unsupported_claims", [])
        
        # Calculate expected improvement
        faithfulness_gap = 1.0 - faithfulness
        
        # Heuristic: Lower temperature reduces hallucination
        if current_temperature > 0.3:
            recommended_temperature = max(current_temperature - 0.3, 0.1)
            expected_improvement = min(faithfulness_gap * 0.6, 0.4)  # Conservative estimate
            
            return {
                "type": "Generation",
                "change": "Lower temperature",
                "current_value": current_temperature,
                "recommended_value": recommended_temperature,
                "expected_effect": f"+{expected_improvement:.2f} faithfulness",
                "rationale": (
                    f"Current faithfulness={faithfulness:.2f} with {len(unsupported_claims)} "
                    f"unsupported claims. Lowering temperature from {current_temperature} to "
                    f"{recommended_temperature} reduces hallucination risk."
                ),
                "confidence": 0.80
            }
        else:
            # Temperature already low, suggest prompt change
            return {
                "type": "Generation",
                "change": "Tighten grounding instruction",
                "current_value": "standard prompt",
                "recommended_value": "strict grounding prompt",
                "expected_effect": f"+{min(faithfulness_gap * 0.5, 0.3):.2f} faithfulness",
                "rationale": (
                    f"Temperature is already low ({current_temperature}), but faithfulness={faithfulness:.2f}. "
                    "Adding explicit grounding instructions would reduce hallucinations."
                ),
                "confidence": 0.70
            }
    
    def _generate_instruction_counterfactual(
        self,
        evaluation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate counterfactual for instruction/prompt failures."""
        
        relevance = evaluation_results.get("relevance", {}).get("relevance", 0.0)
        
        relevance_gap = 1.0 - relevance
        expected_improvement = min(relevance_gap * 0.5, 0.3)
        
        return {
            "type": "Instruction",
            "change": "Revise system prompt",
            "current_value": "restrictive prompt",
            "recommended_value": "flexible prompt",
            "expected_effect": f"+{expected_improvement:.2f} relevance",
            "rationale": (
                f"Current relevance={relevance:.2f}. Prompt may be over-constraining the model. "
                "Revising to encourage direct question answering would improve relevance."
            ),
            "confidence": 0.65
        }
    
    def _generate_query_design_counterfactual(
        self,
        query_feasibility: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate counterfactual for query design issues."""
        
        feasibility_type = query_feasibility.get("feasibility", "Unknown")
        evidence = query_feasibility.get("evidence", {})
        
        if feasibility_type == "OverConstrained":
            return {
                "type": "QueryDesign",
                "change": "Remove constraint",
                "current_value": f"Query with {evidence.get('requested_scope', 'scope')} + {evidence.get('response_constraint', 'format')}",
                "recommended_value": "Query with single constraint",
                "expected_effect": "Query becomes answerable",
                "rationale": (
                    f"Query is over-constrained: {evidence.get('conflict', 'conflicting requirements')}. "
                    f"Removing either scope or format constraint would make it answerable."
                ),
                "confidence": 0.90
            }
        elif feasibility_type == "UnderSpecified":
            return {
                "type": "QueryDesign",
                "change": "Add specificity",
                "current_value": "Vague query",
                "recommended_value": "Specific query with context",
                "expected_effect": "+0.3 relevance, +0.2 recall",
                "rationale": (
                    "Query is too vague. Adding specific details or context would improve "
                    "retrieval precision and answer relevance."
                ),
                "confidence": 0.75
            }
        elif feasibility_type == "OutOfScope":
            return {
                "type": "QueryDesign",
                "change": "Rephrase or add documents",
                "current_value": "Query about missing topics",
                "recommended_value": "Query about covered topics OR add relevant docs",
                "expected_effect": "+0.4 recall",
                "rationale": (
                    f"Query asks about topics not in corpus. Missing concepts: "
                    f"{', '.join(evidence.get('missing_concepts', [])[:3])}. "
                    "Either rephrase query or add documents covering these topics."
                ),
                "confidence": 0.85
            }
        
        return {
            "type": "QueryDesign",
            "change": "No change needed",
            "current_value": "Answerable query",
            "recommended_value": "Answerable query",
            "expected_effect": "N/A",
            "rationale": "Query is well-formed and answerable.",
            "confidence": 0.80
        }
    
    def _generate_context_packing_counterfactual(
        self,
        evaluation_results: Dict[str, Any],
        current_top_k: int,
        current_chunk_size: int
    ) -> Dict[str, Any]:
        """Generate counterfactual for context packing issues."""
        
        recall = evaluation_results.get("context_recall", {}).get("context_recall", 0.0)
        relevance = evaluation_results.get("relevance", {}).get("relevance", 0.0)
        
        # If recall is moderate but relevance is low, reduce noise
        if recall >= 0.5 and relevance < 0.6:
            recommended_top_k = max(current_top_k - 2, 3)
            expected_relevance_gain = min((1.0 - relevance) * 0.4, 0.25)
            
            return {
                "type": "ContextPacking",
                "change": "Reduce top_k",
                "current_value": current_top_k,
                "recommended_value": recommended_top_k,
                "expected_effect": f"+{expected_relevance_gain:.2f} relevance",
                "rationale": (
                    f"Recall={recall:.2f} is adequate but relevance={relevance:.2f} is low. "
                    f"Reducing top_k from {current_top_k} to {recommended_top_k} would "
                    "improve signal-to-noise ratio."
                ),
                "confidence": 0.70
            }
        
        # If both are low, increase chunk overlap
        recommended_overlap = int(current_chunk_size * 0.2)  # 20% overlap
        return {
            "type": "ContextPacking",
            "change": "Increase chunk overlap",
            "current_value": "minimal overlap",
            "recommended_value": f"{recommended_overlap} tokens",
            "expected_effect": "+0.15 recall",
            "rationale": (
                "Increasing chunk overlap would capture more context boundaries, "
                "improving information completeness."
            ),
            "confidence": 0.65
        }
    
    def generate(
        self,
        failure_surface: Optional[str],
        evaluation_results: Dict[str, Any],
        query_feasibility: Optional[Dict[str, Any]] = None,
        current_top_k: int = 5,
        current_chunk_size: int = 500,
        current_temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate counterfactual fix.
        
        Args:
            failure_surface: From Phase B (QueryDesign, Retrieval, etc.)
            evaluation_results: Phase 3 metrics
            query_feasibility: Phase A results (optional)
            current_top_k: Current retrieval parameter
            current_chunk_size: Current chunk size
            current_temperature: Current generation temperature
            
        Returns:
            Dictionary with:
            - counterfactual_fix: The minimal change
            - type: Which component to change
            - change: What to change
            - current_value: Current setting
            - recommended_value: Suggested setting
            - expected_effect: Predicted improvement
            - rationale: Why this would work
            - confidence: 0.0-1.0
        """
        
        if not failure_surface:
            return {
                "counterfactual_fix": None,
                "note": "No failure detected. No counterfactual needed."
            }
        
        # Generate counterfactual based on failure surface
        if failure_surface == "QueryDesign" and query_feasibility:
            fix = self._generate_query_design_counterfactual(query_feasibility)
        elif failure_surface == "Retrieval":
            fix = self._generate_retrieval_counterfactual(
                evaluation_results, current_top_k, current_chunk_size
            )
        elif failure_surface == "Generation":
            fix = self._generate_generation_counterfactual(
                evaluation_results, current_temperature
            )
        elif failure_surface == "Instruction":
            fix = self._generate_instruction_counterfactual(evaluation_results)
        elif failure_surface == "ContextPacking":
            fix = self._generate_context_packing_counterfactual(
                evaluation_results, current_top_k, current_chunk_size
            )
        else:
            return {
                "counterfactual_fix": None,
                "note": f"No counterfactual generator for surface: {failure_surface}"
            }
        
        return {
            "counterfactual_fix": fix
        }
