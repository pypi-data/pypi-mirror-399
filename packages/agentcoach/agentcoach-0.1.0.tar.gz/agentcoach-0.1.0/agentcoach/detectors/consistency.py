"""Consistency detector (MVP stub)."""

from agentcoach.detectors.base import Detector
from agentcoach.models import Finding, FindingCategory, Severity, Trace


class ConsistencyDetector(Detector):
    """Detects consistency issues across multiple runs (MVP stub)."""
    
    @property
    def name(self) -> str:
        return "consistency"
    
    def detect(self, trace: Trace) -> list[Finding]:
        """Detect consistency issues.
        
        MVP: This is a stub implementation. Full consistency checking
        requires multiple trace runs, which is not implemented in this version.
        """
        findings = []
        
        # MVP: Add informational finding about consistency checking
        findings.append(
            Finding(
                category=FindingCategory.CONSISTENCY,
                severity=Severity.INFO,
                message="Consistency detection requires multiple runs (not implemented in MVP)",
                suggested_fixes=[
                    "Run the same input multiple times and compare outputs",
                    "Use semantic similarity to measure consistency",
                    "Implement variance analysis across runs",
                ],
                details={
                    "status": "not_implemented",
                    "note": "This detector is a placeholder for future multi-run consistency analysis",
                },
            )
        )
        
        return findings
