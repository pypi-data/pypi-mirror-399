from typing import Dict, Any, List


class ConflictResolver:
    """
    Phase 6 - Conflict Resolution
    Enforce causal precedence between Answerability → Retrieval → Generation → Prompt.
    """

    def __init__(self, low_threshold: float = 0.5, retrieval_block_threshold: float = 0.45):
        self.low_threshold = low_threshold
        self.retrieval_block_threshold = retrieval_block_threshold

    def _weak_signals(self, evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
        signals = []
        recall = evaluation["context_recall"]["context_recall"]
        faith_data = evaluation["faithfulness"]
        faith = faith_data.get("faithfulness_factual", faith_data.get("faithfulness", 1.0))
        relevance = evaluation["relevance"]["relevance"]

        if recall < self.low_threshold:
            signals.append({"component": "Retrieval", "metric": "recall", "value": recall})
        if faith < self.low_threshold:
            signals.append({"component": "Generation", "metric": "faithfulness", "value": faith})
        if relevance < self.low_threshold:
            signals.append({"component": "Prompt", "metric": "relevance", "value": relevance})
        return signals

    def resolve(
        self,
        evaluation: Dict[str, Any],
        failure_hypothesis: Dict[str, Any],
        answer_intent: Dict[str, Any] = None,
        query_feasibility: Dict[str, Any] = None,
        corpus_concept_check: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Resolve conflicts prioritizing causal order:
        1. Answerability block (query infeasible OR concepts missing from corpus) -> Answerability
        2. Retrieval insufficiency (recall < hard threshold with missing concepts that EXIST in corpus) -> Retrieval
        3. Retrieval weakness (recall < 0.6) -> Retrieval
        4. Generation hallucination (faithfulness_factual low & unsupported claims) -> Generation
        5. Prompt mismatch (relevance low) -> Prompt
        6. Otherwise: Success/ImprovementOpportunity
        """
        primary = failure_hypothesis["primary"]
        faith_data = evaluation["faithfulness"]
        faithfulness = faith_data.get("faithfulness_factual", faith_data.get("faithfulness", 1.0))
        unsupported_claims = faith_data.get(
            "unsupported_factual_claims",
            faith_data.get("unsupported_claims", [])
        )
        recall = evaluation["context_recall"]["context_recall"]
        missing_concepts = evaluation["context_recall"].get("missing_concepts", [])
        relevance = evaluation["relevance"]["relevance"]

        # Check if concepts are missing from corpus (out of scope) vs just not retrieved
        concepts_missing_from_corpus = []
        concepts_in_corpus_but_not_retrieved = []
        if corpus_concept_check:
            concepts_missing_from_corpus = corpus_concept_check.get("concepts_missing_from_corpus", [])
            concepts_in_corpus_but_not_retrieved = corpus_concept_check.get("concepts_in_corpus", [])

        answerability_blocked = (
            query_feasibility
            and query_feasibility.get("feasibility") in {"OverConstrained", "UnderSpecified", "OutOfScope"}
        ) or len(concepts_missing_from_corpus) > 0
        
        # Only consider retrieval issues if concepts exist in corpus but weren't retrieved
        retrieval_gate = (
            recall < self.retrieval_block_threshold 
            and len(concepts_in_corpus_but_not_retrieved) > 0
        )

        gates = {"generation_blame_capped": retrieval_gate}

        if answer_intent and answer_intent.get("intent") == "CorrectAbstention":
            # If concepts are missing from corpus, this is OutOfScope, not Retrieval
            if len(concepts_missing_from_corpus) > 0:
                return {
                    "final_component": "Answerability",
                    "original_component": primary["component"],
                    "confidence": 0.85,
                    "weak_signals": [],
                    "rationale": (
                        f"CorrectAbstention: System correctly refused. Concepts not present in corpus: "
                        f"{', '.join(concepts_missing_from_corpus[:3])}. No retrieval fix can retrieve "
                        "concepts that don't exist. This is OutOfScope."
                    ),
                    "metrics": {
                        "faithfulness": faithfulness,
                        "recall": recall,
                        "relevance": relevance
                    },
                    "gates": gates,
                    "concepts_missing_from_corpus": concepts_missing_from_corpus
                }
            
            # If pipeline continued (should_continue_pipeline=True), retrieval likely needs improvement
            # Check if retrieval should be improved before declaring Success
            if recall < 0.7 and len(concepts_in_corpus_but_not_retrieved) > 0:
                # Correct abstention, but retrieval could be better
                return {
                    "final_component": "Retrieval",
                    "original_component": primary["component"],
                    "confidence": 0.75,
                    "weak_signals": [{"component": "Retrieval", "metric": "recall", "value": recall}],
                    "rationale": (
                        f"CorrectAbstention: System correctly refused, but context_recall={recall:.2f} "
                        f"with {len(concepts_in_corpus_but_not_retrieved)} missing concepts that exist in corpus: "
                        f"{', '.join(concepts_in_corpus_but_not_retrieved[:3])}. Retrieval improvements could "
                        "enable better answers."
                    ),
                    "metrics": {
                        "faithfulness": faithfulness,
                        "recall": recall,
                        "relevance": relevance
                    },
                    "gates": gates
                }
            elif recall < 0.7:
                # Correct abstention, but recall is low (improvement opportunity)
                return {
                    "final_component": "ImprovementOpportunity",
                    "original_component": primary["component"],
                    "confidence": 0.70,
                    "weak_signals": [],
                    "rationale": (
                        f"CorrectAbstention: System correctly refused. "
                        f"Context recall={recall:.2f} could be improved, but no core concepts missing."
                    ),
                    "metrics": {
                        "faithfulness": faithfulness,
                        "recall": recall,
                        "relevance": relevance
                    },
                    "gates": gates
                }
            else:
                # Correct abstention with good retrieval - genuine Success
                return {
                    "final_component": "Success",
                    "original_component": primary["component"],
                    "confidence": answer_intent.get("confidence", 0.9),
                    "weak_signals": [],
                    "rationale": (
                        "Answer is a CorrectAbstention - system correctly refused to answer "
                        "an unanswerable request. Retrieval is adequate. No component is at fault."
                    ),
                    "metrics": {
                        "faithfulness": faithfulness,
                        "recall": recall,
                        "relevance": relevance
                    },
                    "gates": gates
                }

        if answerability_blocked or (query_feasibility and query_feasibility.get("feasibility") == "TyposDetected"):
            rationale = ""
            is_typo = query_feasibility.get("feasibility") == "TyposDetected"
            
            if is_typo:
                typos = query_feasibility.get("evidence", {}).get("suspected_typos", [])
                rationale = (
                    f"Typo detected in query. Suspected typos: {', '.join(typos)}. "
                    "This is a User Query error, not a system failure."
                )
            elif len(concepts_missing_from_corpus) > 0:
                rationale = (
                    f"Concepts not present in corpus: {', '.join(concepts_missing_from_corpus[:3])}. "
                    "No amount of retrieval improvements can retrieve concepts that don't exist. "
                    "This is an OutOfScope query - add relevant documents to the corpus."
                )
            else:
                rationale = (
                    "Query feasibility analysis indicates the question is not answerable "
                    "with the current corpus (OverConstrained/UnderSpecified/OutOfScope)."
                )
            
            return {
                "final_component": "User Query" if is_typo else "Answerability",
                "original_component": primary["component"],
                "confidence": 0.9,
                "weak_signals": [],
                "rationale": rationale,
                "metrics": {
                    "faithfulness": faithfulness,
                    "recall": recall,
                    "relevance": relevance
                },
                "gates": gates,
                "concepts_missing_from_corpus": concepts_missing_from_corpus
            }

        if retrieval_gate:
            return {
                "final_component": "Retrieval",
                "original_component": primary["component"],
                "confidence": 0.88,
                "weak_signals": [{"component": "Retrieval", "metric": "recall", "value": recall}],
                "rationale": (
                    f"Context recall={recall:.2f} below hard threshold with {len(concepts_in_corpus_but_not_retrieved)} "
                    f"missing concepts that EXIST in corpus: {', '.join(concepts_in_corpus_but_not_retrieved[:3])}. "
                    "Retrieval improvements can fix this. Generation blame is capped until retrieval is fixed."
                ),
                "metrics": {
                    "faithfulness": faithfulness,
                    "recall": recall,
                    "relevance": relevance
                },
                "gates": gates
            }

        if recall < 0.6 and len(concepts_in_corpus_but_not_retrieved) > 0:
            return {
                "final_component": "Retrieval",
                "original_component": primary["component"],
                "confidence": 0.8,
                "weak_signals": [{"component": "Retrieval", "metric": "recall", "value": recall}],
                "rationale": (
                    f"Recall={recall:.2f} < 0.6 with {len(concepts_in_corpus_but_not_retrieved)} missing knowledge concepts "
                    f"that exist in corpus: {', '.join(concepts_in_corpus_but_not_retrieved[:3])}. "
                    "Retrieval coverage is insufficient."
                ),
                "metrics": {
                    "faithfulness": faithfulness,
                    "recall": recall,
                    "relevance": relevance
                },
                "gates": gates
            }

        if faithfulness < 0.5 and len(unsupported_claims) > 0:
            return {
                "final_component": "Generation",
                "original_component": primary["component"],
                "confidence": 0.85,
                "weak_signals": [{"component": "Generation", "metric": "faithfulness", "value": faithfulness}],
                "rationale": (
                    f"Faithfulness (factual)={faithfulness:.2f} < 0.5 with {len(unsupported_claims)} "
                    "unsupported factual claims. Generation is hallucinating."
                ),
                "metrics": {
                    "faithfulness": faithfulness,
                    "recall": recall,
                    "relevance": relevance
                },
                "gates": gates
            }

        if relevance < 0.6:
            return {
                "final_component": "Prompt",
                "original_component": primary["component"],
                "confidence": 0.75,
                "weak_signals": [{"component": "Prompt", "metric": "relevance", "value": relevance}],
                "rationale": (
                    f"Relevance={relevance:.2f} < 0.6. Prompt may be restricting or misdirecting the answer."
                ),
                "metrics": {
                    "faithfulness": faithfulness,
                    "recall": recall,
                    "relevance": relevance
                },
                "gates": gates
            }

        if (
            (len(unsupported_claims) > 0 and len(unsupported_claims) <= 2) or
            (faithfulness >= 0.6 and faithfulness < 0.7) or
            (recall >= 0.6 and recall < 0.7)
        ):
            return {
                "final_component": "ImprovementOpportunity",
                "original_component": primary["component"],
                "confidence": 0.7,
                "weak_signals": [],
                "rationale": (
                    f"Answer is mostly correct but has minor issues. "
                    f"Faithfulness={faithfulness:.2f}, recall={recall:.2f}, relevance={relevance:.2f}. "
                    f"Unsupported factual claims: {len(unsupported_claims)}."
                ),
                "metrics": {
                    "faithfulness": faithfulness,
                    "recall": recall,
                    "relevance": relevance
                },
                "note": "Answer is mostly correct; minor grounding improvement possible",
                "gates": gates
            }

        # Success requires ALL metrics to be >= 0.7
        if faithfulness >= 0.7 and recall >= 0.7 and relevance >= 0.7:
            return {
                "final_component": "Success",
                "original_component": primary["component"],
                "confidence": 0.9,
                "weak_signals": [],
                "rationale": (
                    f"All metrics acceptable: faithfulness={faithfulness:.2f}, "
                    f"recall={recall:.2f}, relevance={relevance:.2f}. No failure detected."
                ),
                "metrics": {
                    "faithfulness": faithfulness,
                    "recall": recall,
                    "relevance": relevance
                },
                "gates": gates
            }
        
        # If we get here, metrics are mixed but not meeting any specific failure criteria
        # Default to ImprovementOpportunity rather than Success
        return {
            "final_component": "ImprovementOpportunity",
            "original_component": primary["component"],
            "confidence": 0.65,
            "weak_signals": [],
            "rationale": (
                f"Metrics are mixed: faithfulness={faithfulness:.2f}, "
                f"recall={recall:.2f}, relevance={relevance:.2f}. "
                "Some improvements may be possible."
            ),
            "metrics": {
                "faithfulness": faithfulness,
                "recall": recall,
                "relevance": relevance
            },
            "gates": gates
        }

