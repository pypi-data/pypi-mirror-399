"""Tests for report generation."""

import json
from pathlib import Path

from agentcoach.models import Finding, FindingCategory, Severity, Trace
from agentcoach.report import generate_report


def test_report_generation(tmp_path: Path) -> None:
    """Test that reports are generated correctly."""
    trace = Trace(
        trace_id="test-trace",
        final_answer="Test answer",
    )
    
    findings = [
        Finding(
            category=FindingCategory.SCHEMA,
            severity=Severity.HIGH,
            message="Test finding",
            suggested_fixes=["Fix 1", "Fix 2"],
        )
    ]
    
    output_dir = tmp_path / "reports"
    paths = generate_report(trace, findings, output_dir)
    
    # Check that files were created
    assert paths["json"].exists()
    assert paths["html"].exists()
    
    # Check JSON content
    with open(paths["json"]) as f:
        report = json.load(f)
    
    assert report["metadata"]["trace_id"] == "test-trace"
    assert report["summary"]["total_findings"] == 1
    assert len(report["findings"]) == 1
    assert report["findings"][0]["category"] == "schema"
    
    # Check HTML content
    html_content = paths["html"].read_text()
    assert "AgentCoach Analysis Report" in html_content
    assert "Test finding" in html_content
