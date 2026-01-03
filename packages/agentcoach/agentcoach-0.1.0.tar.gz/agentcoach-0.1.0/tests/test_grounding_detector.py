"""Tests for grounding detector."""

from agentcoach.detectors.grounding import GroundingDetector
from agentcoach.models import FindingCategory, RetrievalEvent, Trace


def test_grounding_detector_no_evidence() -> None:
    """Test that detector skips when no evidence exists."""
    detector = GroundingDetector({})
    trace = Trace(
        trace_id="test",
        final_answer="Some answer",
    )
    
    findings = detector.detect(trace)
    
    # Should not flag issues when no evidence sources exist
    assert len(findings) == 0


def test_grounding_detector_missing_citations() -> None:
    """Test detection of missing citations."""
    detector = GroundingDetector({})
    
    trace = Trace(
        trace_id="test",
        final_answer="Python is a programming language.",
        retrieval_events=[
            RetrievalEvent(
                span_id="span-1",
                query="Python info",
                documents=[
                    {"content": "Python was created by Guido van Rossum in 1991."}
                ],
            )
        ],
    )
    
    findings = detector.detect(trace)
    
    # Should detect lack of citations
    assert len(findings) > 0
    assert any(f.category == FindingCategory.GROUNDING for f in findings)


def test_grounding_detector_with_citations() -> None:
    """Test that citations are recognized."""
    detector = GroundingDetector({})
    
    trace = Trace(
        trace_id="test",
        final_answer="According to the documentation, Python was created by Guido van Rossum [Source: doc1].",
        retrieval_events=[
            RetrievalEvent(
                span_id="span-1",
                query="Python info",
                documents=[
                    {"id": "doc1", "content": "Python was created by Guido van Rossum in 1991."}
                ],
            )
        ],
    )
    
    findings = detector.detect(trace)
    
    # Should not flag major grounding issues
    high_severity = [f for f in findings if f.severity.value in ["critical", "high"]]
    assert len(high_severity) == 0
