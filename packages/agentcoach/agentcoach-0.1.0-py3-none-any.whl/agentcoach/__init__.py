"""AgentCoach: Agent quality analysis and repair SDK."""

from typing import Optional

from agentcoach.models import Finding, Trace
from agentcoach.repair import repair_run
from agentcoach.trace_ingest import load_trace

__version__ = "0.1.0"

__all__ = [
    "Finding",
    "Trace",
    "load_trace",
    "repair_run",
]


def analyze_trace(trace: Trace, config: Optional[dict] = None) -> list[Finding]:
    """Analyze a trace and return findings.
    
    Args:
        trace: The trace to analyze
        config: Optional configuration dictionary
        
    Returns:
        List of findings from all detectors
    """
    from agentcoach.detectors import get_all_detectors
    
    detectors = get_all_detectors(config or {})
    findings = []
    
    for detector in detectors:
        findings.extend(detector.detect(trace))
    
    return findings
