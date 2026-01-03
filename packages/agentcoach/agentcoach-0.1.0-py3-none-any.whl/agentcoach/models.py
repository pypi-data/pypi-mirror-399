"""Core data models for agentcoach."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class SpanKind(str, Enum):
    """Type of span in the trace."""
    LLM = "llm"
    TOOL = "tool"
    RETRIEVAL = "retrieval"
    AGENT = "agent"
    CHAIN = "chain"
    UNKNOWN = "unknown"


class Severity(str, Enum):
    """Severity level for findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingCategory(str, Enum):
    """Category of quality issue."""
    SCHEMA = "schema"
    GROUNDING = "grounding"
    TOOL_USE = "tool_use"
    LOOPS = "loops"
    STATE = "state"
    POLICY_TONE = "policy_tone"
    CONSISTENCY = "consistency"


class Span(BaseModel):
    """A single span in the trace."""
    span_id: str
    parent_span_id: Optional[str] = None
    name: str
    kind: SpanKind = SpanKind.UNKNOWN
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    status: str = "ok"
    
    # Parsed content for specific span types
    llm_prompt: Optional[str] = None
    llm_response: Optional[str] = None
    llm_model: Optional[str] = None
    
    tool_name: Optional[str] = None
    tool_args: Optional[dict[str, Any]] = None
    tool_output: Optional[str] = None
    tool_error: Optional[str] = None
    
    retrieval_query: Optional[str] = None
    retrieval_docs: list[dict[str, Any]] = Field(default_factory=list)


class LLMCall(BaseModel):
    """Extracted LLM call information."""
    span_id: str
    prompt: str
    response: str
    model: Optional[str] = None
    timestamp: Optional[datetime] = None


class ToolCall(BaseModel):
    """Extracted tool call information."""
    span_id: str
    tool_name: str
    args: dict[str, Any]
    output: Optional[str] = None
    error: Optional[str] = None
    timestamp: Optional[datetime] = None


class RetrievalEvent(BaseModel):
    """Extracted retrieval event information."""
    span_id: str
    query: str
    documents: list[dict[str, Any]]
    timestamp: Optional[datetime] = None


class Trace(BaseModel):
    """Complete trace with all spans."""
    trace_id: str
    spans: list[Span] = Field(default_factory=list)
    
    # Extracted structured data
    llm_calls: list[LLMCall] = Field(default_factory=list)
    tool_calls: list[ToolCall] = Field(default_factory=list)
    retrieval_events: list[RetrievalEvent] = Field(default_factory=list)
    
    # Final output
    final_answer: Optional[str] = None
    final_answer_span_id: Optional[str] = None
    
    # User input
    user_input: Optional[str] = None
    
    def get_span(self, span_id: str) -> Optional[Span]:
        """Get a span by ID."""
        for span in self.spans:
            if span.span_id == span_id:
                return span
        return None
    
    def get_root_spans(self) -> list[Span]:
        """Get all root spans (no parent)."""
        return [s for s in self.spans if s.parent_span_id is None]
    
    def get_children(self, span_id: str) -> list[Span]:
        """Get all child spans of a given span."""
        return [s for s in self.spans if s.parent_span_id == span_id]


class Finding(BaseModel):
    """A quality issue found in the trace."""
    category: FindingCategory
    severity: Severity
    message: str
    evidence_span_ids: list[str] = Field(default_factory=list)
    suggested_fixes: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "evidence_span_ids": self.evidence_span_ids,
            "suggested_fixes": self.suggested_fixes,
            "details": self.details,
        }


class RepairResult(BaseModel):
    """Result of a repair operation."""
    success: bool
    original_output: str
    repaired_output: Optional[str] = None
    changes: list[str] = Field(default_factory=list)
    evidence_used: list[str] = Field(default_factory=list)
    error: Optional[str] = None
