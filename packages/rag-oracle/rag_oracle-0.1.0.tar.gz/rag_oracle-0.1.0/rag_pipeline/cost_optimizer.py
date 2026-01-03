from typing import Dict, Any, List
import tiktoken

class CostOptimizer:
    """
    Phase E - Cost-Aware Optimization
    Analyzes retrieval efficiency and recommends cost-saving measures.
    """
    
    def __init__(self, cost_per_1k_tokens: float = 0.002):
        self.cost_per_1k_tokens = cost_per_1k_tokens
        self.enc = tiktoken.get_encoding("cl100k_base")

    def analyze(self, 
                question: str, 
                retrieved_chunks: List[Any], 
                evaluation_results: Dict[str, Any],
                config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the cost efficiency of the query.
        """
        
        # Calculate token usage
        prompt_tokens = len(self.enc.encode(question))
        context_tokens = sum([len(self.enc.encode(c.page_content)) for c in retrieved_chunks])
        total_tokens = prompt_tokens + context_tokens
        
        cost = (total_tokens / 1000) * self.cost_per_1k_tokens
        
        # Analyze wasted context
        # Heuristic: If relevance is low, but we retrieved a lot, it's wasted.
        relevant_chunks_indices = evaluation_results.get("relevance", {}).get("relevant_chunks", [])
        
        # If relevant_chunks is not provided or empty, assume all are wasted if total relevance is low
        relevance_score = evaluation_results.get("relevance", {}).get("relevance", 0.0)
        
        wasted_tokens = 0
        if relevant_chunks_indices:
             for i, chunk in enumerate(retrieved_chunks):
                 if i not in relevant_chunks_indices:
                     wasted_tokens += len(self.enc.encode(chunk.page_content))
        elif relevance_score < 0.3:
             # Assume 80% waste if relevance is garbage
             wasted_tokens = context_tokens * 0.8
             
        wasted_cost = (wasted_tokens / 1000) * self.cost_per_1k_tokens
        
        # Recommendation
        recommendation = "Optimal"
        current_k = config.get("top_k", 5)
        recommended_k = current_k
        
        if wasted_tokens > (context_tokens * 0.5):
             recommendation = "Reduce Top-K"
             recommended_k = max(2, current_k - 2)
        
        return {
            "status": "OptimizationAvailable" if wasted_cost > 0.0001 else "Optimal",
            "total_tokens": total_tokens,
            "total_cost": cost,
            "wasted_tokens": wasted_tokens,
            "wasted_cost": wasted_cost,
            "cost_saving_per_1k_queries": wasted_cost * 1000,
            "recommendation": recommendation,
            "current_top_k": current_k,
            "recommended_top_k": recommended_k
        }
