from typing import Dict, Any, List


class ExactFailurePointDetector:
    """
    Phase 5 - Exact Failure Point Detection
    Convert failure hypotheses into actionable issues + proof statements.
    """

    def __init__(
        self,
        recall_threshold: float = 0.7,
        faith_threshold: float = 0.65,
        relevance_threshold: float = 0.65
    ):
        self.recall_threshold = recall_threshold
        self.faith_threshold = faith_threshold
        self.relevance_threshold = relevance_threshold

    def _build_proof(
        self,
        component: str,
        evaluation: Dict[str, Any],
        config: Dict[str, Any]
    ) -> str:
        if component == "Retrieval":
            recall = evaluation["context_recall"]["context_recall"]
            missing = evaluation["context_recall"].get("missing_concepts", [])
            return (
                f"Recall {recall:.2f} < {self.recall_threshold}; "
                f"missing concepts: {missing}; "
                f"top_k={config.get('top_k')} chunk_size={config.get('chunk_size')}"
            )
        if component == "Generation":
            faith = evaluation["faithfulness"]["faithfulness"]
            return (
                f"Faithfulness {faith:.2f} < {self.faith_threshold}; "
                f"temperature={config.get('temperature')}"
            )
        if component == "Prompt":
            relevance = evaluation["relevance"]["relevance"]
            missing = evaluation["context_recall"].get("missing_concepts", [])
            return (
                f"Relevance {relevance:.2f} < {self.relevance_threshold}; "
                f"missing concepts: {missing}"
            )
        return "All metrics high"

    def detect(
        self,
        evaluation: Dict[str, Any],
        failure_hypothesis: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        hypotheses = [failure_hypothesis["primary"]] + failure_hypothesis.get("alternatives", [])
        points: List[Dict[str, Any]] = []
        for hypothesis in hypotheses:
            component = hypothesis["component"]
            points.append({
                "component": component,
                "exact_issue": (
                    "Retrieval coverage too low" if component == "Retrieval" else
                    "Generation hallucination risk" if component == "Generation" else
                    "Prompt-answer mismatch" if component == "Prompt" else
                    "System is healthy"
                ),
                "proof": self._build_proof(component, evaluation, config),
                "confidence": hypothesis.get("confidence", 0.0),
                "signals": hypothesis.get("signals", {})
            })
        return {
            "exact_failure_points": points,
            "confidence_summary": hypothesis["confidence"] if hypotheses else 0.0
        }

