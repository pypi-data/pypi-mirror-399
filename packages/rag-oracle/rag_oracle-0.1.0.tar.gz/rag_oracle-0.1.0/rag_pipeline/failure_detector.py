from typing import Dict, List, Any


class FailureDetector:
    """
    Phase 4 - Failure Hypothesis
    Detect which components are likely responsible based on evaluation signals,
    allow multiple hypotheses, add confidence scores, and recommend experiments.
    Thresholds and weights are configurable for dynamic behavior.
    """

    def __init__(self, low_threshold: float = 0.5, mid_threshold: float = 0.75):
        self.LOW = low_threshold
        self.MID = mid_threshold
        self.weights = {"faithfulness": 0.4, "recall": 0.35, "relevance": 0.25}

    def _zone(self, value: float) -> str:
        """Convert a metric value into a qualitative zone."""
        if value < self.LOW:
            return "low"
        if value < self.MID:
            return "medium"
        return "high"

    def _confidence(self, metrics: Dict[str, float]) -> float:
        """
        Confidence increases when metrics are far from decision boundaries.
        Uses weighted distance from thresholds.
        """
        total = 0.0
        for key, weight in self.weights.items():
            value = metrics.get(key, 0.0)
            dist = min(abs(value - self.LOW), abs(value - self.MID), abs(value - 1.0))
            total += dist * weight
        normalized = min(1.0, total / sum(self.weights.values()))
        return round(normalized, 2)

    def _categorize(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Produce one or more failure hypotheses with confidence scores."""
        faithfulness = evaluation["faithfulness"]["faithfulness"]
        recall = evaluation["context_recall"]["context_recall"]
        relevance = evaluation["relevance"]["relevance"]

        faith_zone = self._zone(faithfulness)
        recall_zone = self._zone(recall)
        relevance_zone = self._zone(relevance)

        hypotheses = []

        # ---- Retrieval hypothesis ----
        if recall_zone == "low":
            hypotheses.append({
                "component": "Retrieval",
            "confidence": self._confidence({"recall": recall, "faithfulness": faithfulness}),
                "signals": {
                    "recall": recall_zone,
                    "faithfulness": faith_zone,
                    "relevance": relevance_zone
                }
            })

        # ---- Generation hypothesis ----
        if faith_zone == "low" and recall_zone in ("medium", "high"):
            hypotheses.append({
                "component": "Generation",
            "confidence": self._confidence({"faithfulness": faithfulness, "recall": recall}),
                "signals": {
                    "faithfulness": faith_zone,
                    "recall": recall_zone,
                    "relevance": relevance_zone
                }
            })

        # ---- Prompt hypothesis ----
        if relevance_zone == "low" and faith_zone in ("medium", "high"):
            hypotheses.append({
                "component": "Prompt",
            "confidence": self._confidence({"relevance": relevance, "faithfulness": faithfulness}),
                "signals": {
                    "relevance": relevance_zone,
                    "faithfulness": faith_zone,
                    "recall": recall_zone
                }
            })

        # ---- Success case ----
        if (
            faith_zone == "high"
            and recall_zone == "high"
            and relevance_zone == "high"
        ):
            hypotheses.append({
                "component": "Success",
            "confidence": 1.0,
                "signals": {
                    "faithfulness": faith_zone,
                    "recall": recall_zone,
                    "relevance": relevance_zone
                }
            })

        reasoning = [
            f"Faithfulness={faithfulness:.2f} ({faith_zone})",
            f"Recall={recall:.2f} ({recall_zone})",
            f"Relevance={relevance:.2f} ({relevance_zone})",
        ]

        return {
            "failure_hypotheses": hypotheses,
            "reasoning": reasoning,
            "status": "measured"
        }

    def recommend_experiments(self, component: str) -> List[Dict[str, str]]:
        """Recommend experiments based on the suspected component."""
        if component == "Retrieval":
            return [
                {"test": "Increase Top-K", "focus": "Recall improvement"},
                {"test": "Change chunk size", "focus": "Recall improvement"},
                {"test": "Adjust overlap", "focus": "Recall improvement"},
                {"test": "Switch embedding model", "focus": "Recall improvement"},
            ]
        if component == "Generation":
            return [
                {"test": "Lower temperature", "focus": "Faithfulness increase"},
                {"test": "Add grounding instruction", "focus": "Faithfulness increase"},
                {"test": "Switch model", "focus": "Faithfulness increase"},
            ]
        if component == "Prompt":
            return [
                {"test": "Rewrite prompt", "focus": "Relevance improvement"},
                {"test": "Remove summarization bias", "focus": "Relevance improvement"},
                {"test": "Enforce answer format", "focus": "Relevance improvement"},
            ]
        return []

    def detect(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Return failure hypotheses with confidence scores and experiments."""
        analysis = self._categorize(evaluation)

        experiments = []
        for hypothesis in analysis["failure_hypotheses"]:
            experiments.extend(self.recommend_experiments(hypothesis["component"]))

        primary = analysis["failure_hypotheses"][0] if analysis["failure_hypotheses"] else {
            "component": "Unknown",
            "confidence": 0.0,
            "signals": {}
        }

        return {
            "failure_hypothesis": {
                "primary": {
                    "component": primary["component"],
                    "confidence": primary["confidence"],
                    "signals": primary["signals"],
                    "reasoning": analysis["reasoning"]
                },
                "alternatives": analysis["failure_hypotheses"][1:]
            },
            "recommended_experiments": experiments
        }
