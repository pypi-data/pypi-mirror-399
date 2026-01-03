"""
Phase B: Failure Surface Mapper
Maps failures to specific surfaces in the RAG pipeline.
This tells developers WHERE to intervene.
"""

from typing import Dict, Any, List, Optional


class FailureSurfaceMapper:
    """
    Maps failures to specific surfaces in the RAG pipeline.
    
    Failure Surfaces:
    - QueryDesign: User asked impossible/vague/overloaded query
    - Retrieval: Chunks exist but not retrieved
    - ContextPacking: Chunks exist but truncated/diluted
    - Generation: Model ignored or distorted context
    - Instruction: Prompt constrained model incorrectly
    """
    
    def __init__(self):
        """Initialize the mapper."""
        pass
    
    def _analyze_query_design_surface(
        self,
        query_feasibility: Optional[Dict[str, Any]],
        answer_intent: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check if failure is at query design level."""
        
        if not query_feasibility:
            return {"is_surface": False, "confidence": 0.0}
        
        # If query is OverConstrained or UnderSpecified, it's a query design issue
        if query_feasibility.get("feasibility") in ["OverConstrained", "UnderSpecified"]:
            return {
                "is_surface": True,
                "confidence": query_feasibility.get("confidence", 0.85),
                "evidence": query_feasibility.get("evidence", {}),
                "recommendation": query_feasibility.get("recommendation", "")
            }
        
        return {"is_surface": False, "confidence": 0.0}
    
    def _analyze_retrieval_surface(
        self,
        evaluation_results: Dict[str, Any],
        conflict_resolution: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check if failure is at retrieval level."""
        
        recall = evaluation_results.get("context_recall", {}).get("context_recall", 1.0)
        missing_concepts = evaluation_results.get("context_recall", {}).get("missing_concepts", [])
        
        # Issue 2: Detect non-fatal retrieval weakness (CoverageDegradation)
        if recall < 1.0:
            is_fatal = recall < 0.6
            subtype = "FatalRetrievalFailure" if is_fatal else "CoverageDegradation"
            
            blamed_retrieval = False
            if conflict_resolution:
                blamed_retrieval = conflict_resolution.get("final_component") == "Retrieval"
            
            base_confidence = 0.90 if is_fatal else 0.70
            confidence = base_confidence + (0.1 if blamed_retrieval else 0.0)
            
            return {
                "is_surface": True,
                "confidence": min(1.0, confidence),
                "subtype": subtype,
                "severity": "High" if is_fatal else "Low",
                "evidence": {
                    "recall_score": recall,
                    "missing_concepts": missing_concepts,
                    "conflict_resolver_agrees": blamed_retrieval
                },
                "recommendation": (
                    f"Increase top_k or improve indexing. Missing: {', '.join(missing_concepts[:3])}"
                )
            }
        
        return {"is_surface": False, "confidence": 0.0}

    def _analyze_context_packing_surface(
        self,
        evaluation_results: Dict[str, Any],
        num_chunks: int,
        chunk_size: int
    ) -> Dict[str, Any]:
        """Check if failure is due to context packing issues."""
        
        recall = evaluation_results.get("context_recall", {}).get("context_recall", 1.0)
        relevance = evaluation_results.get("relevance", {}).get("relevance", 1.0)
        
        # Signal: Moderate recall but low relevance (chunks found but diluted)
        if 0.5 <= recall <= 0.9 and relevance < 0.75:
            return {
                "is_surface": True,
                "confidence": 0.75,
                "subtype": "ContextDilution",
                "evidence": {
                    "recall_score": recall,
                    "relevance_score": relevance,
                    "num_chunks": num_chunks,
                    "issue": "Relevant chunks retrieved but signal diluted"
                },
                "recommendation": f"Reduce top_k from {num_chunks} to improve signal/noise."
            }
        
        return {"is_surface": False, "confidence": 0.0}

    def _analyze_generation_surface(
        self,
        evaluation_results: Dict[str, Any],
        conflict_resolution: Optional[Dict[str, Any]],
        answer_intent: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check if failure is at generation level."""
        
        faithfulness = evaluation_results.get("faithfulness", {}).get("faithfulness", 1.0)
        unsupported_claims = evaluation_results.get("faithfulness", {}).get("unsupported_claims", [])
        
        # Strong signal: Low faithfulness with unsupported claims
        if faithfulness < 0.6 and len(unsupported_claims) > 0:
            is_hallucination = False
            if answer_intent:
                is_hallucination = answer_intent.get("intent") in ["HallucinatedAnswer", "HallucinatedAbstention"]
            
            blamed_generation = False
            if conflict_resolution:
                blamed_generation = conflict_resolution.get("final_component") == "Generation"
            
            confidence = 0.90 if (is_hallucination or blamed_generation) else 0.75
            
            return {
                "is_surface": True,
                "confidence": confidence,
                "subtype": "Hallucination" if is_hallucination else "Distortion",
                "evidence": {
                    "faithfulness": faithfulness,
                    "unsupported_claims": len(unsupported_claims)
                },
                "recommendation": "Lower temperature or improve grounding instructions."
            }
        
        return {"is_surface": False, "confidence": 0.0}

    def _analyze_instruction_surface(
        self,
        evaluation_results: Dict[str, Any],
        conflict_resolution: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check if failure is due to prompt/instruction issues."""
        
        relevance = evaluation_results.get("relevance", {}).get("relevance", 1.0)
        faithfulness = evaluation_results.get("faithfulness", {}).get("faithfulness", 1.0)
        
        # Signal: Low relevance but high faithfulness (followed prompt too strictly)
        if relevance < 0.7 and faithfulness >= 0.8:
            blamed_prompt = False
            if conflict_resolution:
                blamed_prompt = conflict_resolution.get("final_component") == "Prompt"
            
            confidence = 0.85 if blamed_prompt else 0.70
            
            return {
                "is_surface": True,
                "confidence": confidence,
                "subtype": "InstructionMismatch",
                "evidence": {
                    "relevance": relevance,
                    "faithfulness": faithfulness,
                    "issue": "Model is faithful but not addressing the specific question"
                },
                "recommendation": "Revise system prompt to be less restrictive or more direct."
            }
        
        return {"is_surface": False, "confidence": 0.0}

    def map(
        self,
        evaluation_results: Dict[str, Any],
        query_feasibility: Optional[Dict[str, Any]] = None,
        answer_intent: Optional[Dict[str, Any]] = None,
        conflict_resolution: Optional[Dict[str, Any]] = None,
        num_chunks: int = 5,
        chunk_size: int = 500
    ) -> Dict[str, Any]:
        """
        Map failure to specific surface.
        """
        
        # Check each surface in priority order
        surfaces = [
            ("QueryDesign", self._analyze_query_design_surface(query_feasibility, answer_intent)),
            ("Retrieval", self._analyze_retrieval_surface(evaluation_results, conflict_resolution)),
            ("Generation", self._analyze_generation_surface(evaluation_results, conflict_resolution, answer_intent)),
            ("Instruction", self._analyze_instruction_surface(evaluation_results, conflict_resolution)),
            ("ContextPacking", self._analyze_context_packing_surface(evaluation_results, num_chunks, chunk_size))
        ]
        
        # Find all surfaces that met criteria
        detected_surfaces = []
        for surface_name, analysis in surfaces:
            if analysis["is_surface"]:
                detected_surfaces.append({
                    "failure_surface": surface_name,
                    "subtype": analysis.get("subtype", "Generic"),
                    "severity": analysis.get("severity", "Medium"),
                    "confidence": analysis["confidence"],
                    "evidence": analysis.get("evidence", {}),
                    "recommendation": analysis.get("recommendation", "")
                })
        
        if detected_surfaces:
            # Sort by confidence
            detected_surfaces.sort(key=lambda x: x["confidence"], reverse=True)
            return {
                "failure_surface": detected_surfaces[0]["failure_surface"],
                "subtype": detected_surfaces[0]["subtype"],
                "severity": detected_surfaces[0]["severity"],
                "confidence": detected_surfaces[0]["confidence"],
                "evidence": detected_surfaces[0]["evidence"],
                "recommendation": detected_surfaces[0]["recommendation"],
                "all_detected_surfaces": detected_surfaces # Issue 2 fallback
            }
        
        # No clear failure surface detected
        return {
            "failure_surface": None,
            "confidence": 0.0,
            "evidence": {"note": "No clear failure surface detected. Metrics are acceptable."},
            "recommendation": "System is performing adequately."
        }
