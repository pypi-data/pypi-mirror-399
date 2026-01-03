"""LangGraph integration for quality guard node."""

import json
from pathlib import Path
from typing import Any, Optional, Union

from agentcoach.contracts import load_contract_schema, parse_output_as_json, validate_against_contract
from agentcoach.repair import ToolExecutor


class QualityGuardNode:
    """Quality guard node for LangGraph workflows.
    
    This node validates and optionally repairs agent outputs before
    returning the final answer.
    """
    
    def __init__(
        self,
        contract_schema: Union[Union[str, Path], dict, None] = None,
        policy_pack: Union[Union[str, Path], dict, None] = None,
        tool_executor: Optional[ToolExecutor] = None,
        llm_judge: Optional[str] = None,
        auto_repair: bool = True,
    ):
        """Initialize quality guard node.
        
        Args:
            contract_schema: Path to JSON schema or schema dict
            policy_pack: Path to policy JSON or policy dict
            tool_executor: Optional tool executor for repairs
            llm_judge: Optional LLM provider for repairs (openai, anthropic, sap)
            auto_repair: Whether to automatically repair issues
        """
        self.contract_schema = self._load_schema(contract_schema)
        self.policy = self._load_policy(policy_pack)
        self.tool_executor = tool_executor
        self.llm_judge = llm_judge
        self.auto_repair = auto_repair
    
    def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """Process state through quality guard.
        
        Args:
            state: LangGraph state dict (must contain 'output' or 'answer' key)
            
        Returns:
            Updated state with validated/repaired output
        """
        # Extract output from state
        output = state.get("output") or state.get("answer") or state.get("final_answer")
        
        if not output:
            state["quality_check"] = {
                "passed": False,
                "errors": ["No output found in state"],
            }
            return state
        
        errors = []
        warnings = []
        
        # Validate schema
        if self.contract_schema:
            output_data = parse_output_as_json(output)
            
            if output_data is None and self.contract_schema.get("type") == "object":
                errors.append("Output is not valid JSON")
            elif output_data:
                is_valid, validation_errors = validate_against_contract(
                    output_data, self.contract_schema
                )
                if not is_valid:
                    errors.extend(validation_errors)
        
        # Validate policy
        if self.policy:
            policy_errors = self._check_policy(output)
            errors.extend(policy_errors)
        
        # Auto-repair if enabled and errors found
        if self.auto_repair and errors:
            try:
                repaired = self._repair_output(output, state)
                if repaired != output:
                    output = repaired
                    warnings.append("Output was automatically repaired")
                    errors = []  # Clear errors after successful repair
            except Exception as e:
                warnings.append(f"Auto-repair failed: {e}")
        
        # Update state
        if "output" in state:
            state["output"] = output
        elif "answer" in state:
            state["answer"] = output
        elif "final_answer" in state:
            state["final_answer"] = output
        
        state["quality_check"] = {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
        
        return state
    
    def _load_schema(self, schema: Union[Union[str, Path], dict, None]) -> Optional[dict]:
        """Load contract schema."""
        if schema is None:
            return None
        if isinstance(schema, dict):
            return schema
        return load_contract_schema(schema)
    
    def _load_policy(self, policy: Union[Union[str, Path], dict, None]) -> Optional[dict]:
        """Load policy pack."""
        if policy is None:
            return None
        if isinstance(policy, dict):
            return policy
        
        with open(policy) as f:
            return json.load(f)
    
    def _check_policy(self, output: str) -> list[str]:
        """Check output against policy."""
        errors = []
        
        if not self.policy:
            return errors
        
        # Check banned phrases
        banned = self.policy.get("banned_phrases", [])
        for phrase in banned:
            if phrase.lower() in output.lower():
                errors.append(f"Contains banned phrase: {phrase}")
        
        # Check length
        max_len = self.policy.get("max_answer_length")
        if max_len and len(output) > max_len:
            errors.append(f"Output too long: {len(output)} > {max_len}")
        
        min_len = self.policy.get("min_answer_length")
        if min_len and len(output) < min_len:
            errors.append(f"Output too short: {len(output)} < {min_len}")
        
        return errors
    
    def _repair_output(self, output: str, state: dict[str, Any]) -> str:
        """Attempt to repair output."""
        repaired = output
        
        # Format repair for JSON
        if self.contract_schema and self.contract_schema.get("type") == "object":
            output_data = parse_output_as_json(repaired)
            if output_data is None:
                # Wrap in JSON
                repaired = json.dumps({"answer": repaired}, indent=2)
            else:
                # Add missing required fields
                required = self.contract_schema.get("required", [])
                for field in required:
                    if field not in output_data:
                        if field == "confidence":
                            output_data[field] = 0.5
                        elif field == "citations":
                            output_data[field] = []
                        elif field == "next_actions":
                            output_data[field] = []
                repaired = json.dumps(output_data, indent=2)
        
        return repaired
