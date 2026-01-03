from dataclasses import dataclass
from typing import Optional


@dataclass
class RAGConfig:
    """
    Configuration class for RAG Failure Attribution System thresholds and parameters.
    
    This class centralizes all configurable thresholds used in root cause analysis
    to make the system more maintainable and customizable.
    """
    
    # Typo detection thresholds
    typo_similarity_threshold: float = 0.7
    
    # Recall thresholds
    recall_low_threshold: float = 0.6
    recall_very_low_threshold: float = 0.3
    recall_minimum_threshold: float = 0.5
    
    # Faithfulness thresholds
    faithfulness_low_threshold: float = 0.7
    faithfulness_very_low_threshold: float = 0.8
    
    # Relevance thresholds
    relevance_low_threshold: float = 0.5
    
    # Grounding overlap thresholds
    grounding_high_threshold: float = 0.5
    grounding_medium_threshold: float = 0.3
    grounding_low_threshold: float = 0.2
    grounding_very_low_threshold: float = 0.1
    
    # Query concept overlap thresholds
    query_concept_overlap_high: float = 0.5
    query_concept_overlap_low: float = 0.2
    
    # Counterfactual delta thresholds
    counterfactual_delta_max: float = 0.2
    counterfactual_delta_medium: float = 0.15
    counterfactual_delta_low: float = 0.1
    
    # Answer length thresholds (in tokens, approximate)
    answer_length_short_threshold: int = 30
    
    # Confidence calculation weights
    confidence_recall_weight: float = 0.4
    confidence_grounding_weight: float = 0.4
    confidence_delta_weight: float = 0.2
    
    # Confidence level thresholds for diagnostic maturity
    confidence_high: float = 0.8
    confidence_stable: float = 0.6
    
    # Fix validation thresholds
    fix_validation_min_samples: int = 10
    fix_validation_failure_rate_threshold: float = 0.05
    fix_validation_recall_threshold: float = 0.1
    
    # Report generation thresholds
    report_immediate_window_min: int = 1
    report_immediate_window_max: int = 100
    report_immediate_window_percent: float = 0.1
    
    # System verdict thresholds
    system_healthy_failure_rate: float = 0.2
    system_warning_failure_rate: float = 0.4
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "typo_similarity_threshold": self.typo_similarity_threshold,
            "recall_low_threshold": self.recall_low_threshold,
            "recall_very_low_threshold": self.recall_very_low_threshold,
            "recall_minimum_threshold": self.recall_minimum_threshold,
            "faithfulness_low_threshold": self.faithfulness_low_threshold,
            "faithfulness_very_low_threshold": self.faithfulness_very_low_threshold,
            "relevance_low_threshold": self.relevance_low_threshold,
            "grounding_high_threshold": self.grounding_high_threshold,
            "grounding_medium_threshold": self.grounding_medium_threshold,
            "grounding_low_threshold": self.grounding_low_threshold,
            "grounding_very_low_threshold": self.grounding_very_low_threshold,
            "query_concept_overlap_high": self.query_concept_overlap_high,
            "query_concept_overlap_low": self.query_concept_overlap_low,
            "counterfactual_delta_max": self.counterfactual_delta_max,
            "counterfactual_delta_medium": self.counterfactual_delta_medium,
            "counterfactual_delta_low": self.counterfactual_delta_low,
            "answer_length_short_threshold": self.answer_length_short_threshold,
            "confidence_recall_weight": self.confidence_recall_weight,
            "confidence_grounding_weight": self.confidence_grounding_weight,
            "confidence_delta_weight": self.confidence_delta_weight,
            "confidence_high": self.confidence_high,
            "confidence_stable": self.confidence_stable,
            "fix_validation_min_samples": self.fix_validation_min_samples,
            "fix_validation_failure_rate_threshold": self.fix_validation_failure_rate_threshold,
            "fix_validation_recall_threshold": self.fix_validation_recall_threshold,
            "report_immediate_window_min": self.report_immediate_window_min,
            "report_immediate_window_max": self.report_immediate_window_max,
            "report_immediate_window_percent": self.report_immediate_window_percent,
            "system_healthy_failure_rate": self.system_healthy_failure_rate,
            "system_warning_failure_rate": self.system_warning_failure_rate,
        }


DEFAULT_CONFIG = RAGConfig()

