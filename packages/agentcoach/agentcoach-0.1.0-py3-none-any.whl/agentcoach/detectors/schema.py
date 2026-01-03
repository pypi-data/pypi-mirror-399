"""Schema/contract detector."""

from pathlib import Path
from typing import Any

from agentcoach.contracts import load_contract_schema, parse_output_as_json, validate_against_contract
from agentcoach.detectors.base import Detector
from agentcoach.models import Finding, FindingCategory, Severity, Trace


class SchemaDetector(Detector):
    """Detects output contract/schema violations."""
    
    @property
    def name(self) -> str:
        return "schema"
    
    def detect(self, trace: Trace) -> list[Finding]:
        """Detect schema violations in the final output."""
        findings = []
        
        if not trace.final_answer:
            findings.append(
                Finding(
                    category=FindingCategory.SCHEMA,
                    severity=Severity.CRITICAL,
                    message="No final answer found in trace",
                    suggested_fixes=["Ensure the agent produces a final output"],
                )
            )
            return findings
        
        # Load contract schema if configured
        schema_path = self.config.get("contract_schema")
        if not schema_path:
            # Use default schema
            schema_path = Path(__file__).parent.parent.parent / "schemas" / "default_contract.json"
        
        try:
            schema = load_contract_schema(schema_path)
        except Exception as e:
            findings.append(
                Finding(
                    category=FindingCategory.SCHEMA,
                    severity=Severity.HIGH,
                    message=f"Failed to load contract schema: {e}",
                    suggested_fixes=["Check contract_schema path in configuration"],
                )
            )
            return findings
        
        # Try to parse output as JSON
        output_data = parse_output_as_json(trace.final_answer)
        
        if output_data is None:
            # Output is not JSON - check if schema requires it
            if schema.get("type") == "object":
                findings.append(
                    Finding(
                        category=FindingCategory.SCHEMA,
                        severity=Severity.HIGH,
                        message="Output is not valid JSON but schema expects an object",
                        evidence_span_ids=[trace.final_answer_span_id] if trace.final_answer_span_id else [],
                        suggested_fixes=[
                            "Wrap output in JSON format",
                            "Update prompt to request JSON output",
                            "Add a formatting step to convert output to JSON",
                        ],
                        details={"output_preview": trace.final_answer[:200]},
                    )
                )
            return findings
        
        # Validate against schema
        is_valid, errors = validate_against_contract(output_data, schema)
        
        if not is_valid:
            findings.append(
                Finding(
                    category=FindingCategory.SCHEMA,
                    severity=Severity.HIGH,
                    message=f"Output does not match contract schema: {len(errors)} validation error(s)",
                    evidence_span_ids=[trace.final_answer_span_id] if trace.final_answer_span_id else [],
                    suggested_fixes=[
                        "Add missing required fields",
                        "Fix field types to match schema",
                        "Update prompt to include all required fields",
                        "Add output validation step before final answer",
                    ],
                    details={
                        "validation_errors": errors,
                        "output_data": output_data,
                    },
                )
            )
        
        return findings
