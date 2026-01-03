"""Loop and planning failure detector."""

from collections import defaultdict

from agentcoach.detectors.base import Detector
from agentcoach.models import Finding, FindingCategory, Severity, Trace


class LoopDetector(Detector):
    """Detects infinite loops and planning failures."""
    
    @property
    def name(self) -> str:
        return "loops"
    
    def detect(self, trace: Trace) -> list[Finding]:
        """Detect loop and planning issues."""
        findings = []
        
        max_repeats = self.config.get("detectors", {}).get("loops", {}).get("max_repeats", 3)
        
        # Track repeated tool calls
        tool_call_signatures = defaultdict(list)
        
        for tool_call in trace.tool_calls:
            # Create signature from tool name and args
            signature = (tool_call.tool_name, str(sorted(tool_call.args.items())))
            tool_call_signatures[signature].append(tool_call)
        
        # Check for repeated calls
        for signature, calls in tool_call_signatures.items():
            if len(calls) > max_repeats:
                tool_name = calls[0].tool_name
                findings.append(
                    Finding(
                        category=FindingCategory.LOOPS,
                        severity=Severity.HIGH,
                        message=f"Tool '{tool_name}' called {len(calls)} times with same arguments (possible loop)",
                        evidence_span_ids=[c.span_id for c in calls],
                        suggested_fixes=[
                            "Add loop detection and breaking logic",
                            "Limit maximum retries for the same tool call",
                            "Vary tool arguments or try alternative approaches",
                            "Add explicit termination conditions",
                        ],
                        details={
                            "tool_name": tool_name,
                            "call_count": len(calls),
                            "args": calls[0].args,
                        },
                    )
                )
        
        # Track repeated LLM calls (similar prompts)
        llm_prompts = defaultdict(list)
        for llm_call in trace.llm_calls:
            # Use first 100 chars as signature
            prompt_sig = llm_call.prompt[:100]
            llm_prompts[prompt_sig].append(llm_call)
        
        for prompt_sig, calls in llm_prompts.items():
            if len(calls) > max_repeats:
                findings.append(
                    Finding(
                        category=FindingCategory.LOOPS,
                        severity=Severity.MEDIUM,
                        message=f"Similar LLM prompts repeated {len(calls)} times (possible planning loop)",
                        evidence_span_ids=[c.span_id for c in calls],
                        suggested_fixes=[
                            "Add context or state to break the loop",
                            "Implement explicit planning steps",
                            "Add loop detection in agent logic",
                        ],
                        details={
                            "call_count": len(calls),
                            "prompt_preview": prompt_sig,
                        },
                    )
                )
        
        return findings
