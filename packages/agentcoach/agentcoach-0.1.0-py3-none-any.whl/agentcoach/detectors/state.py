"""State and constraint loss detector."""

from agentcoach.detectors.base import Detector
from agentcoach.models import Finding, FindingCategory, Severity, Trace


class StateDetector(Detector):
    """Detects loss of user constraints or state."""
    
    @property
    def name(self) -> str:
        return "state"
    
    def detect(self, trace: Trace) -> list[Finding]:
        """Detect state and constraint loss issues."""
        findings = []
        
        if not trace.user_input or not trace.final_answer:
            return findings
        
        # Extract potential constraints from user input
        constraints = self._extract_constraints(trace.user_input)
        
        if not constraints:
            return findings
        
        # Check if constraints are present in final answer
        answer_lower = trace.final_answer.lower()
        lost_constraints = []
        
        for constraint in constraints:
            if constraint.lower() not in answer_lower:
                lost_constraints.append(constraint)
        
        if lost_constraints:
            findings.append(
                Finding(
                    category=FindingCategory.STATE,
                    severity=Severity.MEDIUM,
                    message=f"{len(lost_constraints)} user constraint(s) not addressed in final answer",
                    evidence_span_ids=[trace.final_answer_span_id] if trace.final_answer_span_id else [],
                    suggested_fixes=[
                        "Maintain user constraints throughout the agent workflow",
                        "Add explicit constraint tracking in agent state",
                        "Include constraint checklist in final answer validation",
                        "Update prompt to emphasize constraint adherence",
                    ],
                    details={
                        "lost_constraints": lost_constraints,
                        "all_constraints": constraints,
                    },
                )
            )
        
        return findings
    
    def _extract_constraints(self, user_input: str) -> list[str]:
        """Extract potential constraints from user input.
        
        Uses simple heuristics to identify constraint keywords.
        """
        constraints = []
        input_lower = user_input.lower()
        
        # Constraint indicators
        indicators = [
            "must", "should", "need to", "required", "ensure",
            "only", "exactly", "at least", "at most", "maximum",
            "minimum", "between", "within", "limit", "constraint"
        ]
        
        # Split into sentences
        sentences = user_input.replace(".", ".\n").replace("?", "?\n").split("\n")
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(indicator in sentence.lower() for indicator in indicators):
                # Extract the constraint phrase
                if len(sentence) < 200:  # Reasonable constraint length
                    constraints.append(sentence)
        
        return constraints[:10]  # Limit to 10 constraints
