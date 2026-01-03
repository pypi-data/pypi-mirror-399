"""Grounding/evidence detector."""

from agentcoach.detectors.base import Detector
from agentcoach.models import Finding, FindingCategory, Severity, Trace


class GroundingDetector(Detector):
    """Detects lack of evidence grounding in outputs."""
    
    @property
    def name(self) -> str:
        return "grounding"
    
    def detect(self, trace: Trace) -> list[Finding]:
        """Detect grounding issues in the final output."""
        findings = []
        
        if not trace.final_answer:
            return findings
        
        # Check if there are any retrieval or tool events
        has_evidence = len(trace.retrieval_events) > 0 or len(trace.tool_calls) > 0
        
        if not has_evidence:
            # No evidence sources, so grounding check not applicable
            return findings
        
        # Collect all evidence snippets
        evidence_snippets = []
        evidence_span_ids = []
        
        for retrieval in trace.retrieval_events:
            evidence_span_ids.append(retrieval.span_id)
            for doc in retrieval.documents:
                if "content" in doc:
                    evidence_snippets.append(doc["content"])
                elif "snippet" in doc:
                    evidence_snippets.append(doc["snippet"])
        
        for tool_call in trace.tool_calls:
            if tool_call.output and not tool_call.error:
                evidence_span_ids.append(tool_call.span_id)
                evidence_snippets.append(tool_call.output)
        
        if not evidence_snippets:
            findings.append(
                Finding(
                    category=FindingCategory.GROUNDING,
                    severity=Severity.MEDIUM,
                    message="Evidence sources exist but no usable content found",
                    evidence_span_ids=evidence_span_ids,
                    suggested_fixes=[
                        "Ensure retrieval returns document content",
                        "Ensure tools return meaningful outputs",
                    ],
                )
            )
            return findings
        
        # Check if final answer references evidence
        answer_lower = trace.final_answer.lower()
        
        # Look for citation markers
        has_citations = any(
            marker in answer_lower
            for marker in ["[", "source:", "according to", "based on", "reference"]
        )
        
        # Check if answer contains snippets from evidence
        evidence_referenced = False
        for snippet in evidence_snippets:
            if len(snippet) > 20:  # Only check substantial snippets
                # Check for partial matches (at least 15 chars)
                snippet_lower = snippet.lower()
                for i in range(len(snippet_lower) - 15):
                    if snippet_lower[i:i+15] in answer_lower:
                        evidence_referenced = True
                        break
                if evidence_referenced:
                    break
        
        if not has_citations and not evidence_referenced:
            findings.append(
                Finding(
                    category=FindingCategory.GROUNDING,
                    severity=Severity.HIGH,
                    message="Final answer does not reference or cite available evidence",
                    evidence_span_ids=[trace.final_answer_span_id] if trace.final_answer_span_id else [],
                    suggested_fixes=[
                        "Add citations to evidence sources in the answer",
                        "Include relevant quotes or snippets from evidence",
                        "Update prompt to require evidence-based responses",
                        "Add a grounding verification step before final output",
                    ],
                    details={
                        "evidence_count": len(evidence_snippets),
                        "has_citations": has_citations,
                        "evidence_referenced": evidence_referenced,
                    },
                )
            )
        elif not has_citations:
            findings.append(
                Finding(
                    category=FindingCategory.GROUNDING,
                    severity=Severity.MEDIUM,
                    message="Answer uses evidence but lacks explicit citations",
                    evidence_span_ids=[trace.final_answer_span_id] if trace.final_answer_span_id else [],
                    suggested_fixes=[
                        "Add citation markers (e.g., [1], [Source: ...]) to the answer",
                        "Include a references section",
                        "Update prompt to require explicit citations",
                    ],
                    details={
                        "evidence_count": len(evidence_snippets),
                    },
                )
            )
        
        return findings
