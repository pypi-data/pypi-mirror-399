"""Tool use failure detector."""

from collections import defaultdict

from agentcoach.detectors.base import Detector
from agentcoach.models import Finding, FindingCategory, Severity, Trace


class ToolUseDetector(Detector):
    """Detects tool use failures and issues."""
    
    @property
    def name(self) -> str:
        return "tool_use"
    
    def detect(self, trace: Trace) -> list[Finding]:
        """Detect tool use issues."""
        findings = []
        
        if not trace.tool_calls:
            return findings
        
        # Track tool errors
        error_tools = []
        ignored_tools = []
        
        for tool_call in trace.tool_calls:
            # Check for errors
            if tool_call.error:
                error_tools.append(tool_call)
                findings.append(
                    Finding(
                        category=FindingCategory.TOOL_USE,
                        severity=Severity.HIGH,
                        message=f"Tool '{tool_call.tool_name}' failed with error: {tool_call.error}",
                        evidence_span_ids=[tool_call.span_id],
                        suggested_fixes=[
                            "Fix tool arguments to match expected schema",
                            "Handle tool errors gracefully",
                            "Add retry logic with corrected arguments",
                            "Validate tool arguments before execution",
                        ],
                        details={
                            "tool_name": tool_call.tool_name,
                            "args": tool_call.args,
                            "error": tool_call.error,
                        },
                    )
                )
            
            # Check if tool output was ignored (not referenced in final answer)
            elif tool_call.output and trace.final_answer:
                output_snippet = tool_call.output[:100].lower()
                if output_snippet not in trace.final_answer.lower():
                    ignored_tools.append(tool_call)
        
        # Report ignored tool outputs
        if ignored_tools:
            findings.append(
                Finding(
                    category=FindingCategory.TOOL_USE,
                    severity=Severity.MEDIUM,
                    message=f"{len(ignored_tools)} tool output(s) were not used in final answer",
                    evidence_span_ids=[t.span_id for t in ignored_tools],
                    suggested_fixes=[
                        "Ensure tool outputs are incorporated into the answer",
                        "Remove unnecessary tool calls",
                        "Update prompt to use all tool results",
                    ],
                    details={
                        "ignored_tools": [t.tool_name for t in ignored_tools],
                    },
                )
            )
        
        # Check for premature final answer (final answer despite tool errors)
        if error_tools and trace.final_answer:
            # Check if final answer was produced after errors
            last_error_time = max(
                (t.timestamp for t in error_tools if t.timestamp),
                default=None
            )
            
            if last_error_time:
                findings.append(
                    Finding(
                        category=FindingCategory.TOOL_USE,
                        severity=Severity.HIGH,
                        message="Final answer produced despite unresolved tool errors",
                        evidence_span_ids=[trace.final_answer_span_id] if trace.final_answer_span_id else [],
                        suggested_fixes=[
                            "Retry failed tools before producing final answer",
                            "Handle tool errors explicitly in the answer",
                            "Add error recovery logic",
                        ],
                        details={
                            "error_count": len(error_tools),
                        },
                    )
                )
        
        return findings
