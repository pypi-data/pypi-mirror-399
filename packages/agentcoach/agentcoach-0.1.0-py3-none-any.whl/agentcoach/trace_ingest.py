"""Trace ingestion from OpenTelemetry/OpenInference JSON exports."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Union

from agentcoach.models import (
    LLMCall,
    RetrievalEvent,
    Span,
    SpanKind,
    ToolCall,
    Trace,
)


def load_trace(path: Union[str, Path]) -> Trace:
    """Load a trace from a JSON file.
    
    Args:
        path: Path to the trace JSON file
        
    Returns:
        Parsed Trace object
    """
    path = Path(path)
    with open(path) as f:
        data = json.load(f)
    
    return parse_trace(data)


def parse_trace(data: dict[str, Any]) -> Trace:
    """Parse trace data into internal model.
    
    Supports OpenTelemetry and OpenInference formats.
    
    Args:
        data: Raw trace data dictionary
        
    Returns:
        Parsed Trace object
    """
    # Handle different trace formats
    if "resourceSpans" in data:
        # OpenTelemetry format
        return _parse_otel_trace(data)
    elif "spans" in data:
        # Simplified format
        return _parse_simple_trace(data)
    else:
        raise ValueError("Unknown trace format")


def _parse_otel_trace(data: dict[str, Any]) -> Trace:
    """Parse OpenTelemetry format trace."""
    spans = []
    trace_id = None
    
    for resource_span in data.get("resourceSpans", []):
        for scope_span in resource_span.get("scopeSpans", []):
            for span_data in scope_span.get("spans", []):
                span = _parse_otel_span(span_data)
                spans.append(span)
                if trace_id is None:
                    trace_id = span_data.get("traceId", "unknown")
    
    trace = Trace(trace_id=trace_id or "unknown", spans=spans)
    _extract_structured_data(trace)
    return trace


def _parse_simple_trace(data: dict[str, Any]) -> Trace:
    """Parse simplified trace format."""
    spans = []
    
    for span_data in data.get("spans", []):
        span = _parse_simple_span(span_data)
        spans.append(span)
    
    trace = Trace(
        trace_id=data.get("trace_id", "unknown"),
        spans=spans,
    )
    _extract_structured_data(trace)
    return trace


def _parse_otel_span(span_data: dict[str, Any]) -> Span:
    """Parse an OpenTelemetry span."""
    attributes = {}
    for attr in span_data.get("attributes", []):
        key = attr.get("key", "")
        value = attr.get("value", {})
        # Extract value based on type
        if "stringValue" in value:
            attributes[key] = value["stringValue"]
        elif "intValue" in value:
            attributes[key] = value["intValue"]
        elif "doubleValue" in value:
            attributes[key] = value["doubleValue"]
        elif "boolValue" in value:
            attributes[key] = value["boolValue"]
    
    # Determine span kind
    kind = _infer_span_kind(span_data.get("name", ""), attributes)
    
    # Parse timestamps
    start_time = None
    end_time = None
    if "startTimeUnixNano" in span_data:
        start_time = datetime.fromtimestamp(int(span_data["startTimeUnixNano"]) / 1e9)
    if "endTimeUnixNano" in span_data:
        end_time = datetime.fromtimestamp(int(span_data["endTimeUnixNano"]) / 1e9)
    
    span = Span(
        span_id=span_data.get("spanId", ""),
        parent_span_id=span_data.get("parentSpanId"),
        name=span_data.get("name", ""),
        kind=kind,
        start_time=start_time,
        end_time=end_time,
        attributes=attributes,
        status=span_data.get("status", {}).get("code", "ok"),
    )
    
    _populate_span_fields(span)
    return span


def _parse_simple_span(span_data: dict[str, Any]) -> Span:
    """Parse a simplified span format."""
    kind = SpanKind(span_data.get("kind", "unknown"))
    
    # Parse timestamps if present
    start_time = None
    end_time = None
    if "start_time" in span_data:
        start_time = datetime.fromisoformat(span_data["start_time"])
    if "end_time" in span_data:
        end_time = datetime.fromisoformat(span_data["end_time"])
    
    span = Span(
        span_id=span_data.get("span_id", ""),
        parent_span_id=span_data.get("parent_span_id"),
        name=span_data.get("name", ""),
        kind=kind,
        start_time=start_time,
        end_time=end_time,
        attributes=span_data.get("attributes", {}),
        status=span_data.get("status", "ok"),
    )
    
    _populate_span_fields(span)
    return span


def _infer_span_kind(name: str, attributes: dict[str, Any]) -> SpanKind:
    """Infer span kind from name and attributes."""
    name_lower = name.lower()
    
    # Check OpenInference attributes
    if "llm.model_name" in attributes or "gen_ai.system" in attributes:
        return SpanKind.LLM
    if "tool.name" in attributes or "function.name" in attributes:
        return SpanKind.TOOL
    if "retrieval.query" in attributes or "db.statement" in attributes:
        return SpanKind.RETRIEVAL
    
    # Check name patterns
    if any(x in name_lower for x in ["llm", "chat", "completion", "generate"]):
        return SpanKind.LLM
    if any(x in name_lower for x in ["tool", "function", "action"]):
        return SpanKind.TOOL
    if any(x in name_lower for x in ["retrieval", "search", "query", "vector"]):
        return SpanKind.RETRIEVAL
    if any(x in name_lower for x in ["agent", "executor"]):
        return SpanKind.AGENT
    if any(x in name_lower for x in ["chain", "workflow"]):
        return SpanKind.CHAIN
    
    return SpanKind.UNKNOWN


def _populate_span_fields(span: Span) -> None:
    """Populate type-specific fields from attributes."""
    attrs = span.attributes
    
    if span.kind == SpanKind.LLM:
        span.llm_prompt = attrs.get("llm.prompt", attrs.get("input.value", ""))
        span.llm_response = attrs.get("llm.response", attrs.get("output.value", ""))
        span.llm_model = attrs.get("llm.model_name", attrs.get("gen_ai.system", ""))
    
    elif span.kind == SpanKind.TOOL:
        span.tool_name = attrs.get("tool.name", attrs.get("function.name", span.name))
        span.tool_args = attrs.get("tool.args", attrs.get("function.arguments", {}))
        span.tool_output = attrs.get("tool.output", attrs.get("output.value", ""))
        span.tool_error = attrs.get("tool.error", attrs.get("exception.message", ""))
    
    elif span.kind == SpanKind.RETRIEVAL:
        span.retrieval_query = attrs.get("retrieval.query", attrs.get("db.statement", ""))
        docs = attrs.get("retrieval.documents", attrs.get("documents", []))
        if isinstance(docs, list):
            span.retrieval_docs = docs


def _extract_structured_data(trace: Trace) -> None:
    """Extract structured data from spans."""
    llm_calls = []
    tool_calls = []
    retrieval_events = []
    
    for span in trace.spans:
        if span.kind == SpanKind.LLM and span.llm_prompt and span.llm_response:
            llm_calls.append(
                LLMCall(
                    span_id=span.span_id,
                    prompt=span.llm_prompt,
                    response=span.llm_response,
                    model=span.llm_model,
                    timestamp=span.start_time,
                )
            )
        
        elif span.kind == SpanKind.TOOL and span.tool_name:
            tool_calls.append(
                ToolCall(
                    span_id=span.span_id,
                    tool_name=span.tool_name,
                    args=span.tool_args or {},
                    output=span.tool_output,
                    error=span.tool_error,
                    timestamp=span.start_time,
                )
            )
        
        elif span.kind == SpanKind.RETRIEVAL and span.retrieval_query:
            retrieval_events.append(
                RetrievalEvent(
                    span_id=span.span_id,
                    query=span.retrieval_query,
                    documents=span.retrieval_docs,
                    timestamp=span.start_time,
                )
            )
    
    trace.llm_calls = llm_calls
    trace.tool_calls = tool_calls
    trace.retrieval_events = retrieval_events
    
    # Extract final answer and user input
    _extract_final_answer(trace)
    _extract_user_input(trace)


def _extract_final_answer(trace: Trace) -> None:
    """Extract the final answer from the trace."""
    # Look for spans marked as final or with output
    for span in reversed(trace.spans):
        if span.kind == SpanKind.AGENT or "final" in span.name.lower():
            answer = span.attributes.get("output.value", span.attributes.get("answer", ""))
            if answer:
                trace.final_answer = answer
                trace.final_answer_span_id = span.span_id
                return
    
    # Fallback: use last LLM response
    if trace.llm_calls:
        last_call = trace.llm_calls[-1]
        trace.final_answer = last_call.response
        trace.final_answer_span_id = last_call.span_id


def _extract_user_input(trace: Trace) -> None:
    """Extract the user input from the trace."""
    # Look for root spans with input
    for span in trace.get_root_spans():
        user_input = span.attributes.get("input.value", span.attributes.get("query", ""))
        if user_input:
            trace.user_input = user_input
            return
    
    # Fallback: use first LLM prompt
    if trace.llm_calls:
        trace.user_input = trace.llm_calls[0].prompt
