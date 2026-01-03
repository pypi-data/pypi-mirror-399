"""Tests for schema detector."""

import pytest

from agentcoach.detectors.schema import SchemaDetector
from agentcoach.models import FindingCategory, Severity, Trace


def test_schema_detector_missing_answer() -> None:
    """Test detection of missing final answer."""
    detector = SchemaDetector({})
    trace = Trace(trace_id="test", final_answer=None)
    
    findings = detector.detect(trace)
    
    assert len(findings) == 1
    assert findings[0].category == FindingCategory.SCHEMA
    assert findings[0].severity == Severity.CRITICAL
    assert "No final answer" in findings[0].message


def test_schema_detector_invalid_json() -> None:
    """Test detection of invalid JSON when schema expects object."""
    detector = SchemaDetector({
        "contract_schema": None,  # Will use default schema
    })
    
    trace = Trace(
        trace_id="test",
        final_answer="This is plain text, not JSON",
        final_answer_span_id="span-1",
    )
    
    findings = detector.detect(trace)
    
    # Should find that output is not JSON
    assert len(findings) > 0
    assert any("not valid JSON" in f.message for f in findings)


def test_schema_detector_valid_json() -> None:
    """Test that valid JSON passes schema check."""
    detector = SchemaDetector({})
    
    trace = Trace(
        trace_id="test",
        final_answer='{"answer": "Test answer", "confidence": 0.9}',
        final_answer_span_id="span-1",
    )
    
    findings = detector.detect(trace)
    
    # Should pass or only have minor issues
    critical_findings = [f for f in findings if f.severity == Severity.CRITICAL]
    assert len(critical_findings) == 0
