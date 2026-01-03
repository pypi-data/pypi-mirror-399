"""
Concept Type Separator
Separates knowledge concepts from instruction/constraint tokens for accurate recall calculation.
"""

from typing import List, Dict, Set, Any
import re


class ConceptTypeSeparator:
    """
    Separates concepts into knowledge concepts vs instruction/constraint tokens.
    
    This prevents pollution of "missing concepts" with instruction words like
    "explain", "short", "sentence" which are NOT retrieval targets.
    """
    
    # Instruction/constraint tokens to ignore for recall
    INSTRUCTION_TOKENS = {
    # Format / task instructions
    "explain", "list", "describe", "summarize", "define", "outline",
    "compare", "contrast", "analyze", "evaluate", "discuss",
    "interpret", "review", "breakdown", "classify", "identify",
    "generate", "create", "write", "rewrite", "edit", "improve",
    "optimize", "translate", "rephrase", "simplify", "elaborate",

    # Constraints / length / structure
    "short", "long", "brief", "detailed", "simple", "complex",
    "sentence", "sentences", "paragraph", "paragraphs",
    "word", "words", "point", "points", "step", "steps",
    "one", "two", "three", "four", "five",
    "all", "every", "each", "some", "any", "few", "many",
    "exactly", "approximately", "minimum", "maximum",

    # Question / auxiliary verbs
    "what", "how", "why", "when", "where", "who", "which", "whom",
    "is", "are", "was", "were", "be", "been", "being",
    "do", "does", "did", "doing",
    "can", "could", "should", "would", "will", "shall", "may", "might",
    "have", "has", "had",

    # Meta / prompt control words
    "please", "kindly", "tell", "give", "show", "provide",
    "according", "based", "from", "about", "regarding",
    "include", "excluding", "without", "using", "use",
    "example", "examples", "sample", "samples",
    "format", "structure", "style", "tone",

    # Comparison / logic helpers
    "vs", "versus", "difference", "differences", "similarity", "similarities",
    "pros", "cons", "advantages", "disadvantages",
    "reason", "reasons", "cause", "effect",

    # Common stopwords
    "the", "a", "an", "and", "or", "but",
    "if", "else", "then", "than",
    "in", "on", "at", "to", "for", "of", "with", "by", "as",
    "this", "that", "these", "those",
    "it", "its", "they", "them", "their",
    "we", "you", "your", "i", "me", "my"
}


    # Explicit whitelist for words that look like instructions but are core RAG concepts
    DOMAIN_KNOWLEDGE_WHITELIST = {
        "probability", "mindset", "thinking", "strategy", "discipline", "market", "trading"
    }
    
    def __init__(self):
        """Initialize the separator."""
        self.instruction_tokens = self.INSTRUCTION_TOKENS
    
    def _get_concept_confidence(self, concept: str) -> float:
        """
        Calculates a confidence score for a concept being a 'knowledge' concept.
        Issue 1: Prevent 0.0 recall by allowing granular confidence.
        """
        concept_lower = concept.lower().strip()
        
        # 0.0 for pure instructions
        if concept_lower in self.instruction_tokens:
            return 0.0
            
        # 1.0 for whitelisted domain terms
        if concept_lower in self.DOMAIN_KNOWLEDGE_WHITELIST:
            return 1.0
            
        score = 0.5 # Base score
        
        # Boost for length
        if len(concept_lower) > 5: score += 0.2
        if len(concept_lower) > 10: score += 0.1
        
        # Boost for multi-word concepts (proper phrases)
        if " " in concept_lower: score += 0.2
        
        # Boost for casing (proper nouns)
        if concept[0].isupper() and not concept_lower in self.instruction_tokens:
            score += 0.1
            
        return min(1.0, score)

    def separate_concepts(self, concepts: List[str]) -> Dict[str, Any]:
        """
        Separate concepts into knowledge concepts vs instruction tokens with confidence.
        """
        knowledge_data = [] # List of dicts {text, confidence}
        instruction_tokens = []
        
        for concept in concepts:
            confidence = self._get_concept_confidence(concept)
            
            if confidence >= 0.5:
                knowledge_data.append({
                    "text": concept,
                    "confidence": confidence
                })
            elif confidence == 0.0:
                instruction_tokens.append(concept)
            else:
                # Low confidence knowledge - still include but mark it
                knowledge_data.append({
                    "text": concept,
                    "confidence": confidence
                })
        
        return {
            "knowledge_concepts": [k["text"] for k in knowledge_data],
            "knowledge_metadata": knowledge_data,
            "instruction_tokens": instruction_tokens,
            "all_concepts": concepts
        }
    
    def filter_knowledge_concepts(self, concepts: List[str]) -> List[str]:
        """
        Filter concepts to only knowledge concepts (convenience method).
        """
        separated = self.separate_concepts(concepts)
        return separated["knowledge_concepts"]
