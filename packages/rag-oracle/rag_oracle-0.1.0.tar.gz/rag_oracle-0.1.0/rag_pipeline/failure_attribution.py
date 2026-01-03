from typing import Dict, Any, List


class FailureAttributionEngine:
    """
    Phase 7 - Failure Attribution Engine
    Combine prior phases but enforce causal hierarchy:
    Answerability → Retrieval → Generation → Prompt.
    """

    def __init__(self, retrieval_block_threshold: float = 0.45):
        self.retrieval_block_threshold = retrieval_block_threshold

    def attribute(
        self,
        failure_detection: Dict[str, Any],
        exact_failure_point: Dict[str, Any],
        conflict_resolution: Dict[str, Any],
        evaluation_results: Dict[str, Any] = None,
        failure_surface: Dict[str, Any] = None,
        query_feasibility: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        transcripts: List[str] = []
        primary = failure_detection["failure_hypothesis"]["primary"]
        alternatives = failure_detection["failure_hypothesis"].get("alternatives", [])

        transcripts.append(
            f"Phase4 primary={primary['component']} conf={primary.get('confidence'):.2f}"
        )
        if alternatives:
            transcripts.append(
                f"Phase4 alternatives={[s['component'] for s in alternatives]}"
            )
        transcripts.append(f"Phase6 verdict={conflict_resolution['final_component']}")
        transcripts.append(
            f"Phase5 points={[p['component'] for p in exact_failure_point['exact_failure_points']]}"
        )

        final_component = conflict_resolution["final_component"]
        confidence = conflict_resolution.get("confidence", 0.0) or 0.0

        recall = None
        missing = []
        if evaluation_results:
            recall = evaluation_results.get("context_recall", {}).get("context_recall")
            missing = evaluation_results.get("context_recall", {}).get("missing_concepts", [])
        faithfulness = None
        if evaluation_results:
            faithfulness = evaluation_results.get("faithfulness", {}).get("faithfulness", None)

        answerability_blocked = (
            query_feasibility
            and query_feasibility.get("feasibility") in {"OverConstrained", "UnderSpecified", "OutOfScope"}
        )
        retrieval_surface_flag = (
            failure_surface
            and failure_surface.get("failure_surface") == "Retrieval"
            and failure_surface.get("confidence", 0.0) >= 0.75
        )
        retrieval_gate = (
            recall is not None
            and recall < self.retrieval_block_threshold
            and missing
        )

        override_notes: List[str] = []
        primary_failure = final_component
        secondary_failure = alternatives[0]["component"] if alternatives else "None"

        if final_component == "User Query":
             primary_failure = "User Query"
        elif answerability_blocked:
            primary_failure = "Answerability"
            override_notes.append(
                f"Phase A feasibility marked query as {query_feasibility.get('feasibility')}."
            )
        elif retrieval_gate and final_component != "Answerability" and final_component != "User Query":
            if final_component != "Retrieval":
                override_notes.append(
                    f"Recall={recall:.2f} with {len(missing)} missing concepts triggered retrieval precedence."
                )
            primary_failure = "Retrieval"
        elif retrieval_surface_flag and final_component != "Retrieval":
            override_notes.append(
                f"Phase B mapped failure surface to Retrieval ({failure_surface.get('subtype')})."
            )
            primary_failure = "Retrieval"

        if primary_failure != final_component:
            if final_component not in {"Success", "ImprovementOpportunity"}:
                secondary_failure = final_component

        confidence = round(max(confidence, 0.82 if override_notes else confidence), 2)

        if not override_notes and primary_failure == "ImprovementOpportunity" and alternatives:
            secondary_failure = alternatives[0]["component"]

        result = {
            "primary_failure": primary_failure,
            "secondary_risk": secondary_failure,
            "confidence": confidence,
            "history": transcripts
        }
        if override_notes:
            result["override_notes"] = override_notes
        if faithfulness is not None:
            result["metrics_snapshot"] = {
                "faithfulness": faithfulness,
                "recall": recall,
                "missing_concepts": missing
            }
        return result

