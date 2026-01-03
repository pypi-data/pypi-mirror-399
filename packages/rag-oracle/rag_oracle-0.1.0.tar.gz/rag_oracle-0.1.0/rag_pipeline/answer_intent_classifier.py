"""
Answer Intent Classifier
Classifies the type of answer to distinguish correct abstentions from failures.
"""

from typing import Dict, Any, List
import re


class AnswerIntentClassifier:
    """
    Classifies answer intent to prevent misclassifying correct abstentions as failures.
    
    Answer Types:
    - CorrectAbstention: System correctly refused with NO unsupported claims
    - HallucinatedAbstention: System refused but made false claims about the context
    - FullAnswer: Complete answer provided
    - PartialAnswer: Incomplete but valid answer
    - HallucinatedAnswer: Answer contains unsupported claims
    """
    
    # STRONG abstention phrases (clear refusals)
    STRONG_ABSTENTION_PHRASES = [
        "does not contain enough information",
        "context does not mention",
        "cannot be answered from the provided context",
        "not enough information to answer",
        "cannot answer this question",
        "information is not available in the context",
        "not found in the context",
        "missing from the context",
    ]
    
    # WEAK abstention phrases (might be in partial answers)
    WEAK_ABSTENTION_PHRASES = [
        "does not provide",
        "doesn't contain",
        "doesn't mention",
        "cannot determine",
        "not specified",
    ]
    
    def __init__(self):
        """Initialize the classifier."""
        pass
    
    def _contains_abstention_phrase(self, answer: str) -> Dict[str, Any]:
        """
        Check if answer contains abstention phrases.
        
        Args:
            answer: The generated answer
            
        Returns:
            Dictionary with:
            - has_abstention: True if found
            - strength: "strong" or "weak"
            - phrase: The matched phrase
        """
        answer_lower = answer.lower()
        
        # Check for strong abstention phrases first
        for phrase in self.STRONG_ABSTENTION_PHRASES:
            if phrase in answer_lower:
                return {
                    "has_abstention": True,
                    "strength": "strong",
                    "phrase": phrase
                }
        
        # Check for weak abstention phrases
        for phrase in self.WEAK_ABSTENTION_PHRASES:
            if phrase in answer_lower:
                return {
                    "has_abstention": True,
                    "strength": "weak",
                    "phrase": phrase
                }
        
        return {"has_abstention": False, "strength": None, "phrase": None}
    
    def classify(self, answer: str, evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify the answer intent.
        
        Args:
            answer: The generated answer
            evaluation_results: Results from Phase 3 evaluation
            
        Returns:
            Dictionary with:
            - intent: CorrectAbstention | HallucinatedAbstention | FullAnswer | PartialAnswer | HallucinatedAnswer
            - confidence: 0.0-1.0
            - reasoning: Explanation of classification
            - should_continue_pipeline: Whether to continue with failure detection
        """
        faithfulness_data = evaluation_results.get("faithfulness", {})
        faithfulness_score = faithfulness_data.get(
            "faithfulness_factual",
            faithfulness_data.get("faithfulness", 0.0)
        )
        relevance_score = evaluation_results.get("relevance", {}).get("relevance", 0.0)
        context_recall_score = evaluation_results.get("context_recall", {}).get("context_recall", 1.0)
        unsupported_claims = faithfulness_data.get(
            "unsupported_factual_claims",
            faithfulness_data.get("unsupported_claims", [])
        )
        
        # PRIORITY 1: Check for abstention phrases FIRST
        abstention_check = self._contains_abstention_phrase(answer)
        
        if abstention_check["has_abstention"]:
            abstention_strength = abstention_check["strength"]
            
            # STRONG abstention phrases = clear refusal
            if abstention_strength == "strong":
                # REFINED RULE: Allow up to 1 unsupported claim for CorrectAbstention
                # Why? The evaluator often treats the abstention statement itself as an "unsupported claim"
                if len(unsupported_claims) <= 1:
                    # Even if abstention is correct, check if retrieval could be improved
                    should_continue = context_recall_score < 0.7
                    return {
                        "intent": "CorrectAbstention",
                        "confidence": 0.95 if len(unsupported_claims) == 0 else 0.90,
                        "reasoning": (
                            f"Answer contains STRONG abstention phrase ('{abstention_check['phrase']}') "
                            f"with {len(unsupported_claims)} unsupported claim(s) (≤1). "
                            f"This is a correct refusal. "
                            f"Faithfulness={faithfulness_score:.2f}, relevance={relevance_score:.2f}, "
                            f"context_recall={context_recall_score:.2f}."
                            + (" Retrieval could be improved." if should_continue else "")
                        ),
                        "should_continue_pipeline": should_continue  # Continue if retrieval is poor
                    }
                else:
                    # Strong abstention but multiple unsupported claims = hallucinating while refusing
                    return {
                        "intent": "HallucinatedAbstention",
                        "confidence": 0.85,
                        "reasoning": (
                            f"Answer contains abstention phrase BUT has {len(unsupported_claims)} "
                            f"unsupported claims (>1). System is refusing while hallucinating. "
                            f"Faithfulness={faithfulness_score:.2f}."
                        ),
                        "should_continue_pipeline": True  # Continue to blame Generation
                    }
            
            # WEAK abstention phrases = might be partial answer with limitations
            elif abstention_strength == "weak":
                # Check if answer is substantive despite the weak abstention phrase
                answer_length = len(answer)
                
                # If answer is long (>100 chars) AND has good metrics, it's a PartialAnswer
                if (answer_length > 100 and 
                    faithfulness_score >= 0.7 and 
                    relevance_score >= 0.7):
                    return {
                        "intent": "PartialAnswer",
                        "confidence": 0.80,
                        "reasoning": (
                            f"Answer contains weak abstention phrase but is substantive ({answer_length} chars). "
                            f"Faithfulness={faithfulness_score:.2f}, relevance={relevance_score:.2f}. "
                            "This is a partial answer acknowledging limitations, not a refusal."
                        ),
                        "should_continue_pipeline": True  # May need improvements
                    }
                
                # Otherwise, treat as CorrectAbstention if claims are low
                elif len(unsupported_claims) <= 1:
                    # Even if abstention is correct, check if retrieval could be improved
                    should_continue = context_recall_score < 0.7
                    return {
                        "intent": "CorrectAbstention",
                        "confidence": 0.85,
                        "reasoning": (
                            f"Answer contains weak abstention phrase with {len(unsupported_claims)} "
                            f"unsupported claim(s). Treating as correct refusal. "
                            f"Faithfulness={faithfulness_score:.2f}, relevance={relevance_score:.2f}, "
                            f"context_recall={context_recall_score:.2f}."
                            + (" Retrieval could be improved." if should_continue else "")
                        ),
                        "should_continue_pipeline": should_continue  # Continue if retrieval is poor
                    }
        
        # PRIORITY 2: Check for HallucinatedAnswer (only if NOT an abstention)
        # Require BOTH low faithfulness AND actual unsupported claims
        if len(unsupported_claims) > 2 and faithfulness_score < 0.6:
            return {
                "intent": "HallucinatedAnswer",
                "confidence": 0.85,
                "reasoning": (
                    f"Answer has {len(unsupported_claims)} unsupported claims "
                    f"and faithfulness={faithfulness_score:.2f} < 0.6. "
                    "This is a hallucination issue."
                ),
                "should_continue_pipeline": True  # Continue to blame Generation
            }
        
        # PRIORITY 3: Check for FullAnswer
        if faithfulness_score >= 0.7 and relevance_score >= 0.7:
            # Even if answer is good, check if retrieval can be improved
            if context_recall_score < 0.7:
                return {
                    "intent": "FullAnswer",
                    "confidence": 0.85,
                    "reasoning": (
                        f"Faithfulness={faithfulness_score:.2f} and relevance={relevance_score:.2f} "
                        f"are both high, but context_recall={context_recall_score:.2f} is low. "
                        "Answer is good but retrieval could be improved."
                    ),
                    "should_continue_pipeline": True  # Continue to suggest retrieval improvements
                }
            else:
                return {
                    "intent": "FullAnswer",
                    "confidence": 0.9,
                    "reasoning": (
                        f"Faithfulness={faithfulness_score:.2f}, relevance={relevance_score:.2f}, "
                        f"and context_recall={context_recall_score:.2f} are all high. "
                        "This is a successful answer."
                    ),
                    "should_continue_pipeline": False  # Success - no fixes needed
                }
        
        # PRIORITY 4: Check for PartialAnswer
        if relevance_score >= 0.5 and relevance_score < 0.75:
            return {
                "intent": "PartialAnswer",
                "confidence": 0.7,
                "reasoning": (
                    f"Relevance={relevance_score:.2f} is moderate (0.5-0.75). "
                    "Answer is partial but may be valid given constraints."
                ),
                "should_continue_pipeline": True  # May need fixes
            }
        
        # Default: Continue pipeline for potential issues
        return {
            "intent": "PartialAnswer",
            "confidence": 0.6,
            "reasoning": (
                f"Metrics are mixed (faithfulness={faithfulness_score:.2f}, "
                f"relevance={relevance_score:.2f}). Continuing pipeline for analysis."
            ),
            "should_continue_pipeline": True
        }
