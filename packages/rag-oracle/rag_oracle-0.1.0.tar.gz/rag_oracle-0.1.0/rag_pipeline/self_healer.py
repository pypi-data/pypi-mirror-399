from typing import Dict, Any, Callable, Optional, List


class SelfHealer:
    """
    Phase 9 - Self Healing
    Re-run critical steps with the recommended fix to measure improvement.
    Supports Retrieval, Generation, and Prompt fixes.
    Tries multiple candidates until one improves metrics or all are exhausted.
    """

    def __init__(self, retriever_getter: Callable[[], Any], evaluator, generator_getter: Optional[Callable[[], Any]] = None):
        self.retriever_getter = retriever_getter
        self.evaluator = evaluator
        self.generator_getter = generator_getter

    def heal(self, question: str, fix: Dict[str, Any], baseline_eval: Dict[str, Any], baseline_chunks: Optional[Any] = None, experiment_table: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Apply the recommended fix and re-evaluate to measure improvement.
        If the first fix doesn't help, try next candidates from experiment_table.
        
        Args:
            question: The original question
            fix: The recommended fix from Phase 8
            baseline_eval: Baseline evaluation results
            baseline_chunks: Baseline retrieved chunks (for generation/prompt fixes)
            experiment_table: List of all candidate fixes from Phase 8 (optional)
        """
        component = fix.get("component", "Unknown")
        param = fix["parameter"]
        recommended = fix["recommended"]
        
        if component == "Retriever":
            return self._heal_retrieval_with_fallback(question, fix, baseline_eval, experiment_table)
        elif component == "Generator":
            return self._heal_generation_with_fallback(question, fix, baseline_eval, baseline_chunks, experiment_table)
        elif component == "Prompt":
            return self._heal_prompt_with_fallback(question, fix, baseline_eval, baseline_chunks, experiment_table)
        else:
            return {"message": f"Self-heal does not support component: {component}"}

    def _heal_retrieval_with_fallback(self, question: str, fix: Dict[str, Any], baseline_eval: Dict[str, Any], experiment_table: Optional[List[Dict]]) -> Dict[str, Any]:
        """Try retrieval fixes until one improves or all are exhausted."""
        if fix["parameter"] != "top_k":
            return {"message": f"Retrieval self-heal currently supports top_k only (got {fix['parameter']})."}
        
        retriever = self.retriever_getter()
        if not retriever:
            return {"message": "Self-heal skipped: retriever unavailable."}
        
        baseline_recall = baseline_eval["context_recall"]["context_recall"]
        baseline_missing = baseline_eval["context_recall"].get("missing_concepts", [])
        
        candidates_to_try = [fix]
        if experiment_table:
            for candidate in experiment_table:
                if candidate.get("param") == "top_k" and candidate.get("recommended") != fix["recommended"]:
                    candidates_to_try.append({
                        "component": "Retriever",
                        "parameter": candidate["param"],
                        "recommended": candidate["recommended"],
                        "current": candidate.get("current")
                    })
        
        best_result = None
        for candidate_fix in candidates_to_try:
            result = self._heal_retrieval(question, candidate_fix["parameter"], candidate_fix["recommended"], baseline_eval)
            if result.get("message"):
                continue
            
            delta_recall = result.get("delta_recall", 0)
            
            if delta_recall > 0:
                result["tried_candidates"] = len(candidates_to_try[:candidates_to_try.index(candidate_fix) + 1])
                return result
            
            if best_result is None or delta_recall > best_result.get("delta_recall", -999):
                best_result = result
                best_result["tried_candidates"] = len(candidates_to_try[:candidates_to_try.index(candidate_fix) + 1])
        
        if best_result:
            best_result["note"] = "No candidate improved recall, returning best attempt"
        return best_result or {"message": "All retrieval candidates failed"}

    def _heal_generation_with_fallback(self, question: str, fix: Dict[str, Any], baseline_eval: Dict[str, Any], baseline_chunks: Optional[Any], experiment_table: Optional[List[Dict]]) -> Dict[str, Any]:
        """Try generation fixes until one improves or all are exhausted."""
        generator = self.generator_getter() if self.generator_getter else None
        if not generator:
            return {"message": "Self-heal skipped: generator unavailable."}
        
        if not baseline_chunks:
            return {"message": "Self-heal skipped: baseline chunks required for generation fixes."}
        
        baseline_faithfulness = baseline_eval["faithfulness"]["faithfulness"]
        baseline_unsupported = len(
            baseline_eval["faithfulness"].get(
                "unsupported_factual_claims",
                baseline_eval["faithfulness"].get("unsupported_claims", [])
            )
        )
        
        candidates_to_try = [fix]
        if experiment_table:
            for candidate in experiment_table:
                candidate_param = candidate.get("param")
                if candidate_param in ["temperature", "system_prompt"]:
                    candidate_value = candidate.get("recommended")  # Phase 8 uses "recommended" in results
                    if candidate_value is None:
                        continue
                    # Check if this candidate is different from the recommended fix
                    candidate_fix_dict = {
                        "component": "Generator",
                        "parameter": candidate_param,
                        "recommended": candidate_value,
                        "current": candidate.get("current")
                    }
                    # Only add if it's different from the first fix
                    if not any(
                        c["parameter"] == candidate_fix_dict["parameter"] and 
                        c["recommended"] == candidate_fix_dict["recommended"]
                        for c in candidates_to_try
                    ):
                        candidates_to_try.append(candidate_fix_dict)
        
        best_result = None
        for candidate_fix in candidates_to_try:
            result = self._heal_generation(question, candidate_fix["parameter"], candidate_fix["recommended"], baseline_eval, baseline_chunks)
            if result.get("message"):
                continue
            
            delta_faithfulness = result.get("delta_faithfulness", 0)
            
            if delta_faithfulness > 0:
                result["tried_candidates"] = len(candidates_to_try[:candidates_to_try.index(candidate_fix) + 1])
                return result
            
            if best_result is None or delta_faithfulness > best_result.get("delta_faithfulness", -999):
                best_result = result
                best_result["tried_candidates"] = len(candidates_to_try[:candidates_to_try.index(candidate_fix) + 1])
        
        if best_result:
            best_result["note"] = "No candidate improved faithfulness, returning best attempt"
        return best_result or {"message": "All generation candidates failed"}

    def _heal_prompt_with_fallback(self, question: str, fix: Dict[str, Any], baseline_eval: Dict[str, Any], baseline_chunks: Optional[Any], experiment_table: Optional[List[Dict]]) -> Dict[str, Any]:
        """Try prompt fixes until one improves or all are exhausted."""
        generator = self.generator_getter() if self.generator_getter else None
        if not generator:
            return {"message": "Self-heal skipped: generator unavailable."}
        
        if not baseline_chunks:
            return {"message": "Self-heal skipped: baseline chunks required for prompt fixes."}
        
        baseline_relevance = baseline_eval["relevance"]["relevance"]
        
        candidates_to_try = [fix]
        if experiment_table:
            for candidate in experiment_table:
                candidate_param = candidate.get("param")
                if candidate_param in ["system_prompt", "user_prompt"]:
                    candidate_value = candidate.get("recommended")  # Phase 8 uses "recommended" in results
                    if candidate_value is None:
                        continue
                    candidate_fix_dict = {
                        "component": "Prompt",
                        "parameter": candidate_param,
                        "recommended": candidate_value,
                        "current": candidate.get("current")
                    }
                    # Only add if it's different from the first fix
                    if not any(
                        c["parameter"] == candidate_fix_dict["parameter"] and 
                        str(c["recommended"]) == str(candidate_fix_dict["recommended"])
                        for c in candidates_to_try
                    ):
                        candidates_to_try.append(candidate_fix_dict)
        
        best_result = None
        for candidate_fix in candidates_to_try:
            result = self._heal_prompt(question, candidate_fix["parameter"], candidate_fix["recommended"], baseline_eval, baseline_chunks)
            if result.get("message"):
                continue
            
            delta_relevance = result.get("delta_relevance", 0)
            
            if delta_relevance > 0:
                result["tried_candidates"] = len(candidates_to_try[:candidates_to_try.index(candidate_fix) + 1])
                return result
            
            if best_result is None or delta_relevance > best_result.get("delta_relevance", -999):
                best_result = result
                best_result["tried_candidates"] = len(candidates_to_try[:candidates_to_try.index(candidate_fix) + 1])
        
        if best_result:
            best_result["note"] = "No candidate improved relevance, returning best attempt"
        return best_result or {"message": "All prompt candidates failed"}

    def _heal_retrieval(self, question: str, param: str, recommended: Any, baseline_eval: Dict[str, Any]) -> Dict[str, Any]:
        """Apply retrieval fix and re-evaluate."""
        retriever = self.retriever_getter()
        if not retriever:
            return {"message": "Retriever unavailable."}
        
        baseline_recall = baseline_eval["context_recall"]["context_recall"]
        baseline_missing = baseline_eval["context_recall"].get("missing_concepts", [])
        
        chunks = retriever.retrieve(question, top_k=recommended)
        recall_eval = self.evaluator.evaluate_context_recall(question, chunks)
        recall = recall_eval["context_recall"]
        delta = round(recall - baseline_recall, 2)
        missing = recall_eval.get("missing_concepts", [])
        resolved = [c for c in baseline_missing if c not in missing]
        
        return {
            "component": "Retriever",
            "parameter": param,
            "self_heal_recall": recall,
            "delta_recall": delta,
            "missing_concepts": missing,
            "missing_concepts_resolved": resolved,
            "fix": {"parameter": param, "recommended": recommended}
        }

    def _heal_generation(self, question: str, param: str, recommended: Any, baseline_eval: Dict[str, Any], baseline_chunks: Optional[Any]) -> Dict[str, Any]:
        """Apply generation fix and re-evaluate."""
        generator = self.generator_getter() if self.generator_getter else None
        if not generator:
            return {"message": "Generator unavailable."}
        
        if not baseline_chunks:
            return {"message": "Baseline chunks required."}
        
        baseline_faithfulness = baseline_eval["faithfulness"]["faithfulness"]
        baseline_unsupported = len(
            baseline_eval["faithfulness"].get(
                "unsupported_factual_claims",
                baseline_eval["faithfulness"].get("unsupported_claims", [])
            )
        )
        
        original_temp = generator.temperature
        original_system = generator.system_prompt
        
        try:
            if param == "temperature":
                generator.update_temperature(recommended)
            elif param == "system_prompt":
                generator.update_system_prompt(recommended)
            else:
                return {"message": f"Unsupported parameter: {param}"}
            
            answer, _ = generator.generate(question, baseline_chunks)
            faith_eval = self.evaluator.evaluate_faithfulness(
                answer,
                baseline_chunks,
                question=question
            )
            faithfulness = faith_eval["faithfulness"]
            unsupported = len(
                faith_eval.get("unsupported_factual_claims", faith_eval.get("unsupported_claims", []))
            )
            delta = round(faithfulness - baseline_faithfulness, 2)
            
            result = {
                "component": "Generator",
                "parameter": param,
                "self_heal_faithfulness": faithfulness,
                "delta_faithfulness": delta,
                "unsupported_claims": unsupported,
                "unsupported_claims_delta": unsupported - baseline_unsupported,
                "fix": {"parameter": param, "recommended": recommended}
            }
            
            if param == "temperature":
                generator.update_temperature(original_temp)
            elif param == "system_prompt":
                generator.update_system_prompt(original_system)
            
            return result
        except Exception as e:
            if param == "temperature":
                try:
                    generator.update_temperature(original_temp)
                except:
                    pass
            elif param == "system_prompt":
                try:
                    generator.update_system_prompt(original_system)
                except:
                    pass
            return {"message": f"Self-heal failed: {str(e)}"}

    def _heal_prompt(self, question: str, param: str, recommended: Any, baseline_eval: Dict[str, Any], baseline_chunks: Optional[Any]) -> Dict[str, Any]:
        """Apply prompt fix and re-evaluate."""
        generator = self.generator_getter() if self.generator_getter else None
        if not generator:
            return {"message": "Generator unavailable."}
        
        if not baseline_chunks:
            return {"message": "Baseline chunks required."}
        
        baseline_relevance = baseline_eval["relevance"]["relevance"]
        
        original_system = generator.system_prompt
        
        try:
            if param == "system_prompt":
                generator.update_system_prompt(recommended)
                answer, _ = generator.generate(question, baseline_chunks)
                generator.update_system_prompt(original_system)
            elif param == "user_prompt":
                custom_prompt = recommended
                answer, _ = generator.generate(question, baseline_chunks, custom_prompt=custom_prompt)
            else:
                return {"message": f"Unsupported parameter: {param}"}
            
            relevance_eval = self.evaluator.evaluate_relevance(question, answer)
            relevance = relevance_eval["relevance"]
            delta = round(relevance - baseline_relevance, 2)
            
            return {
                "component": "Prompt",
                "parameter": param,
                "self_heal_relevance": relevance,
                "delta_relevance": delta,
                "fix": {"parameter": param, "recommended": recommended}
            }
        except Exception as e:
            if param == "system_prompt":
                try:
                    generator.update_system_prompt(original_system)
                except:
                    pass
            return {"message": f"Self-heal failed: {str(e)}"}
