"""Policy and tone compliance detector."""

import json
from pathlib import Path

from agentcoach.detectors.base import Detector
from agentcoach.models import Finding, FindingCategory, Severity, Trace


class PolicyToneDetector(Detector):
    """Detects policy and tone violations."""
    
    @property
    def name(self) -> str:
        return "policy_tone"
    
    def detect(self, trace: Trace) -> list[Finding]:
        """Detect policy and tone issues."""
        findings = []
        
        if not trace.final_answer:
            return findings
        
        # Load policy configuration
        policy = self._load_policy()
        
        if not policy:
            return findings
        
        answer = trace.final_answer
        answer_lower = answer.lower()
        
        # Check banned phrases
        banned_phrases = policy.get("banned_phrases", [])
        found_banned = []
        
        for phrase in banned_phrases:
            if phrase.lower() in answer_lower:
                found_banned.append(phrase)
        
        if found_banned:
            findings.append(
                Finding(
                    category=FindingCategory.POLICY_TONE,
                    severity=Severity.HIGH,
                    message=f"Output contains {len(found_banned)} banned phrase(s)",
                    evidence_span_ids=[trace.final_answer_span_id] if trace.final_answer_span_id else [],
                    suggested_fixes=[
                        "Remove or rephrase banned phrases",
                        "Add post-processing filter for banned content",
                        "Update prompt to avoid these phrases",
                    ],
                    details={
                        "banned_phrases_found": found_banned,
                    },
                )
            )
        
        # Check answer length
        max_length = policy.get("max_answer_length")
        min_length = policy.get("min_answer_length")
        
        if max_length and len(answer) > max_length:
            findings.append(
                Finding(
                    category=FindingCategory.POLICY_TONE,
                    severity=Severity.MEDIUM,
                    message=f"Answer exceeds maximum length ({len(answer)} > {max_length})",
                    evidence_span_ids=[trace.final_answer_span_id] if trace.final_answer_span_id else [],
                    suggested_fixes=[
                        "Trim answer to meet length requirements",
                        "Update prompt to request concise responses",
                        "Add length validation before final output",
                    ],
                    details={
                        "actual_length": len(answer),
                        "max_length": max_length,
                    },
                )
            )
        
        if min_length and len(answer) < min_length:
            findings.append(
                Finding(
                    category=FindingCategory.POLICY_TONE,
                    severity=Severity.MEDIUM,
                    message=f"Answer below minimum length ({len(answer)} < {min_length})",
                    evidence_span_ids=[trace.final_answer_span_id] if trace.final_answer_span_id else [],
                    suggested_fixes=[
                        "Expand answer with more details",
                        "Update prompt to request comprehensive responses",
                    ],
                    details={
                        "actual_length": len(answer),
                        "min_length": min_length,
                    },
                )
            )
        
        return findings
    
    def _load_policy(self) -> dict:
        """Load policy configuration."""
        policy_path = self.config.get("policy")
        
        if not policy_path:
            # Use default policy
            policy_path = Path(__file__).parent.parent.parent / "schemas" / "default_policy.json"
        
        try:
            with open(policy_path) as f:
                return json.load(f)
        except Exception:
            return {}
