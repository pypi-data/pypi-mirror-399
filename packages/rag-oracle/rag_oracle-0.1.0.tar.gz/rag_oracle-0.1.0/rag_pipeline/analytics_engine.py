from typing import List, Dict, Any
import json
import statistics
from collections import Counter
from pathlib import Path

class AnalyticsEngine:
    """
    Phase F - Trend Analytics
    Aggregates logs to generate system-wide health reports.
    """
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        
    def generate_report(self) -> Dict[str, Any]:
        """Scan all log files and aggregate metrics."""
        log_files = list(self.log_dir.glob("query_*.json"))
        
        # Filter for valid logs (containing diagnostic data)
        valid_logs = []
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    diagnostics = {}
                    if "evaluation" in data:
                        diagnostics = data 
                    elif "trace" in data and "evaluation" in data["trace"]:
                        diagnostics = data["trace"] 
                    elif "evaluation_results" in data:
                         diagnostics = {"evaluation": data["evaluation_results"]}
                    
                    if diagnostics.get("evaluation"):
                        valid_logs.append(data)
            except:
                continue
                
        total_queries = len(valid_logs)
        
        if total_queries == 0:
            return {"message": "No queries with diagnostic data found. Run example_usage.py first."}
            
        failures = []
        metrics = {"faithfulness": [], "recall": [], "relevance": []}
        
        failed_queries = []
        
        wasted_spend = 0.0
        
        for data in valid_logs:
            # Normalize structure
            diag = data
            if "trace" in data: diag = data["trace"]
            
            # Metrics
            eval_res = diag.get("evaluation", {})
            metrics["faithfulness"].append(eval_res.get("faithfulness", {}).get("faithfulness", 0))
            metrics["recall"].append(eval_res.get("context_recall", {}).get("context_recall", 0))
            metrics["relevance"].append(eval_res.get("relevance", {}).get("relevance", 0))
            
            # Failures - Use Phase 7 or Phase 4
            primary = "Unknown"
            if "failure_attribution" in diag:
                primary = diag["failure_attribution"].get("primary_failure", "Unknown")
            elif "failure_detection" in diag:
                primary = diag["failure_detection"].get("failure_hypothesis", {}).get("primary", {}).get("component", "Unknown")
                
            if primary not in ["Success", "Unknown", None]:
                # STRICT CHECK: Only count as failure if Outcome is FAILURE or (legacy) Faithfulness is low
                is_failure = False
                outcome = diag.get("outcome")
                
                if outcome == "FAILURE":
                    is_failure = True
                elif not outcome:
                    # Legacy fallback: Trust metrics, not just attribution presence
                    f_score = eval_res.get("faithfulness", {}).get("faithfulness", 1.0)
                    r_score = eval_res.get("relevance", {}).get("relevance", 1.0)
                    if f_score < 0.7 or r_score < 0.5:
                        is_failure = True

                if is_failure:
                    failures.append(primary)
                
                # Get specific reason
                reason = "Unknown"
                if "exact_failure_point" in diag:
                    points = diag["exact_failure_point"].get("exact_failure_points", [])
                    if points and len(points) > 0:
                        reason = points[0].get("exact_issue", "Unknown")
                    
                # Construct fix message
                fix_msg = "None"
                p8 = diag.get("phase8_recommendation", {})
                if "recommended_fix" in p8:
                    rf = p8["recommended_fix"]
                    fix_msg = f"{rf.get('component')}->{rf.get('parameter')}: {rf.get('current')}->{rf.get('recommended')}"
                elif "message" in p8:
                    fix_msg = p8["message"]

                failed_queries.append({
                    "id": data.get("query_id", "unknown"),
                    "question": data.get("question", "unknown"),
                    "failure": primary,
                    "reason": reason,
                    "fix_suggested": fix_msg
                })
                
            # Cost Analysis
            if "cost_optimization" in diag:
                wasted_spend += diag["cost_optimization"].get("wasted_cost", 0.0)

        # Aggregation
        fail_counts = Counter(failures)
        
        # Strategic Recommendations
        recommendations = []
        if fail_counts.get("Retrieval", 0) > (total_queries * 0.3):
             recommendations.append("High retrieval failure rate detected. Consider increasing top_k or chunk_size globally.")
        
        # Identify recurring triggers
        triggers = {}
        for f in failed_queries:
             if f["fix_suggested"] != "None":
                 param = f["fix_suggested"].split(":")[0]
                 triggers[param] = triggers.get(param, 0) + 1
        
        for param, count in triggers.items():
            if count > 1:
                recommendations.append(f"Parameter '{param}' triggered fixes in {count} queries. Consider updating system default.")

        return {
            "total_queries": total_queries,
            "failure_rate": round(len(failures) / total_queries, 2),
            "avg_quality_score": round(
                (statistics.mean(metrics["faithfulness"]) + statistics.mean(metrics["recall"])) / 2, 2
            ),
            "metric_trends": {k: round(statistics.mean(v), 2) for k, v in metrics.items()},
            "top_failure_drivers": dict(fail_counts.most_common(3)),
            "strategic_recommendations": recommendations,
            "top_failed_queries": failed_queries[-5:], # Last 5 failures
            "financial_impact": {
                "wasted_spend_detected": f"${wasted_spend:.4f}",
                "projected_annual_waste": f"${wasted_spend * 10 * 365:.2f} (assuming 10 q/day)"
            }
        }
