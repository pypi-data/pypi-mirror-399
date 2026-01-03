"""Runtime repair and guard functionality."""

import json
from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol, Union

from agentcoach.contracts import parse_output_as_json, validate_against_contract
from agentcoach.models import RepairResult, Trace


class ToolExecutor(Protocol):
    """Protocol for tool execution."""
    
    def execute(self, tool_name: str, args: dict[str, Any]) -> str:
        """Execute a tool and return its output."""
        ...


def repair_run(
    trace: Trace,
    contract_schema: Optional[dict[str, Any]] = None,
    tool_executor: Optional[ToolExecutor] = None,
    llm_provider: Optional[str] = None,
) -> RepairResult:
    """Repair a trace run based on detected issues.
    
    Args:
        trace: The trace to repair
        contract_schema: Optional contract schema to enforce
        tool_executor: Optional tool executor for rerunning failed tools
        llm_provider: Optional LLM provider for content repair (openai, anthropic, sap)
        
    Returns:
        RepairResult with original and repaired outputs
    """
    if not trace.final_answer:
        return RepairResult(
            success=False,
            original_output="",
            error="No final answer in trace",
        )
    
    original = trace.final_answer
    repaired = original
    changes = []
    evidence_used = []
    
    # Step 1: Format repair (ensure JSON if schema requires it)
    if contract_schema:
        output_data = parse_output_as_json(repaired)
        
        if output_data is None and contract_schema.get("type") == "object":
            # Try to wrap in JSON
            repaired_data = {"answer": repaired}
            repaired = json.dumps(repaired_data, indent=2)
            changes.append("Wrapped output in JSON format")
            output_data = repaired_data
        
        # Validate and add missing required fields
        if output_data:
            is_valid, errors = validate_against_contract(output_data, contract_schema)
            if not is_valid:
                # Add missing required fields with defaults
                required = contract_schema.get("required", [])
                for field in required:
                    if field not in output_data:
                        if field == "confidence":
                            output_data[field] = 0.5
                        elif field == "citations":
                            output_data[field] = []
                        elif field == "next_actions":
                            output_data[field] = []
                        else:
                            output_data[field] = ""
                        changes.append(f"Added missing required field: {field}")
                
                repaired = json.dumps(output_data, indent=2)
    
    # Step 2: Grounding repair (rewrite using only evidence)
    if trace.retrieval_events or trace.tool_calls:
        evidence_snippets = []
        
        for retrieval in trace.retrieval_events:
            for doc in retrieval.documents:
                if "content" in doc:
                    evidence_snippets.append(doc["content"])
                    evidence_used.append(f"retrieval:{retrieval.span_id}")
        
        for tool_call in trace.tool_calls:
            if tool_call.output and not tool_call.error:
                evidence_snippets.append(tool_call.output)
                evidence_used.append(f"tool:{tool_call.tool_name}")
        
        # If LLM provider available, use it for grounding repair
        if llm_provider and evidence_snippets:
            try:
                from agentcoach.judge import get_judge
                judge = get_judge(llm_provider)
                
                grounded_answer = judge.rewrite_with_evidence(
                    original_answer=repaired,
                    evidence=evidence_snippets,
                    user_query=trace.user_input or "",
                )
                
                if grounded_answer and grounded_answer != repaired:
                    repaired = grounded_answer
                    changes.append("Rewrote answer to use only provided evidence")
            except Exception as e:
                changes.append(f"Grounding repair failed: {e}")
    
    # Step 3: Tool rerun (if executor provided)
    if tool_executor:
        for tool_call in trace.tool_calls:
            if tool_call.error:
                # Suggest corrected args (simplified - in production would use LLM)
                changes.append(
                    f"Tool '{tool_call.tool_name}' failed - manual correction needed"
                )
    
    success = len(changes) > 0
    
    return RepairResult(
        success=success,
        original_output=original,
        repaired_output=repaired if success else None,
        changes=changes,
        evidence_used=evidence_used,
    )
