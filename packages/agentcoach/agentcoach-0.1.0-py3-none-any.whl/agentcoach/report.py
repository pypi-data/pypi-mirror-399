"""Report generation for analysis results."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Union

from jinja2 import Template

from agentcoach.models import Finding, Trace


def generate_report(
    trace: Trace,
    findings: list[Finding],
    output_dir: Union[str, Path],
    include_recommendations: bool = True
) -> dict[str, Path]:
    """Generate JSON and HTML reports.
    
    Args:
        trace: The analyzed trace
        findings: List of findings from detectors
        output_dir: Directory to write reports to
        include_recommendations: Whether to include engineering recommendations
        
    Returns:
        Dictionary mapping report type to file path
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build report data
    report_data = _build_report_data(trace, findings, include_recommendations)
    
    # Generate JSON report
    json_path = output_dir / "report.json"
    with open(json_path, "w") as f:
        json.dump(report_data, f, indent=2, default=str)
    
    # Generate HTML report
    html_path = output_dir / "report.html"
    html_content = _generate_html_report(report_data)
    with open(html_path, "w") as f:
        f.write(html_content)
    
    return {
        "json": json_path,
        "html": html_path,
    }


def _build_report_data(
    trace: Trace,
    findings: list[Finding],
    include_recommendations: bool
) -> dict[str, Any]:
    """Build structured report data."""
    # Group findings by category and severity
    by_category: dict[str, list[Finding]] = {}
    by_severity: dict[str, list[Finding]] = {}
    
    for finding in findings:
        cat = finding.category.value
        sev = finding.severity.value
        
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(finding)
        
        if sev not in by_severity:
            by_severity[sev] = []
        by_severity[sev].append(finding)
    
    # Calculate summary scores
    severity_weights = {"critical": 10, "high": 5, "medium": 2, "low": 1, "info": 0}
    total_score = sum(severity_weights.get(f.severity.value, 0) for f in findings)
    max_possible = len(findings) * 10 if findings else 1
    quality_score = max(0, 100 - (total_score / max_possible * 100))
    
    # Generate recommendations
    recommendations = []
    if include_recommendations:
        recommendations = _generate_recommendations(trace, findings)
    
    return {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "version": "0.1.0",
            "trace_id": trace.trace_id,
        },
        "summary": {
            "total_findings": len(findings),
            "by_severity": {k: len(v) for k, v in by_severity.items()},
            "by_category": {k: len(v) for k, v in by_category.items()},
            "quality_score": round(quality_score, 1),
        },
        "trace_info": {
            "span_count": len(trace.spans),
            "llm_calls": len(trace.llm_calls),
            "tool_calls": len(trace.tool_calls),
            "retrieval_events": len(trace.retrieval_events),
            "has_final_answer": trace.final_answer is not None,
        },
        "findings": [f.to_dict() for f in findings],
        "recommendations": recommendations,
    }


def _generate_recommendations(trace: Trace, findings: list[Finding]) -> list[dict[str, Any]]:
    """Generate engineering recommendations from findings."""
    recommendations = []
    
    # Group findings by category
    by_category: dict[str, list[Finding]] = {}
    for finding in findings:
        cat = finding.category.value
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(finding)
    
    # Schema issues -> prompt engineering
    if "schema" in by_category:
        recommendations.append({
            "type": "prompt_engineering",
            "title": "Add Output Schema to Prompt",
            "description": "Include the expected JSON schema in the system prompt",
            "priority": "high",
            "diff": """
--- system_prompt
+++ system_prompt
 You are a helpful assistant.
+
+Always format your final response as JSON with these fields:
+{
+  "answer": "your answer here",
+  "confidence": 0.0-1.0,
+  "citations": [{"source": "...", "snippet": "..."}]
+}
""",
        })
    
    # Grounding issues -> retrieval settings
    if "grounding" in by_category:
        recommendations.append({
            "type": "retrieval_settings",
            "title": "Improve Retrieval Configuration",
            "description": "Adjust retrieval parameters to improve evidence quality",
            "priority": "high",
            "suggestions": [
                "Increase top_k from 3 to 5-10 for more evidence",
                "Add re-ranking step to prioritize relevant documents",
                "Implement query rewriting for better retrieval",
                "Include document metadata in retrieval results",
            ],
        })
        
        recommendations.append({
            "type": "prompt_engineering",
            "title": "Enforce Citation Requirements",
            "description": "Update prompt to require explicit citations",
            "priority": "medium",
            "diff": """
--- system_prompt
+++ system_prompt
 Provide a comprehensive answer based on the retrieved documents.
+
+IMPORTANT: You MUST cite your sources using [Source: X] notation.
+Include relevant quotes from the documents to support your answer.
""",
        })
    
    # Tool use issues -> error handling
    if "tool_use" in by_category:
        recommendations.append({
            "type": "error_handling",
            "title": "Add Tool Error Recovery",
            "description": "Implement retry logic and error handling for tool calls",
            "priority": "high",
            "code_snippet": """
# Add to your agent workflow
def call_tool_with_retry(tool_name, args, max_retries=2):
    for attempt in range(max_retries + 1):
        try:
            result = execute_tool(tool_name, args)
            return result
        except Exception as e:
            if attempt < max_retries:
                # Optionally use LLM to fix args
                args = fix_tool_args(tool_name, args, error=str(e))
            else:
                return {"error": str(e)}
""",
        })
    
    # Loop issues -> termination logic
    if "loops" in by_category:
        recommendations.append({
            "type": "architecture",
            "title": "Add Loop Detection and Breaking",
            "description": "Implement explicit loop detection in agent logic",
            "priority": "high",
            "code_snippet": """
# Track tool call history
tool_history = []
MAX_SAME_CALL = 3

def should_break_loop(tool_name, args):
    signature = (tool_name, str(args))
    count = tool_history.count(signature)
    return count >= MAX_SAME_CALL

# Before each tool call
if should_break_loop(tool_name, args):
    return "Loop detected, trying alternative approach"
""",
        })
    
    # Policy/tone issues -> add validation node
    if "policy_tone" in by_category:
        recommendations.append({
            "type": "architecture",
            "title": "Add Policy Validation Node",
            "description": "Add a final validation step to check policy compliance",
            "priority": "medium",
            "code_snippet": """
# Add as final node in LangGraph
from agentcoach.langgraph import QualityGuardNode

quality_guard = QualityGuardNode(
    contract_schema="path/to/schema.json",
    policy_pack="path/to/policy.json"
)

# In your graph definition
graph.add_node("quality_guard", quality_guard)
graph.add_edge("draft_answer", "quality_guard")
graph.add_edge("quality_guard", END)
""",
        })
    
    # Memory trimming for long traces
    if len(trace.llm_calls) > 10:
        recommendations.append({
            "type": "memory_management",
            "title": "Implement Memory Trimming",
            "description": "Reduce context size to prevent token limit issues",
            "priority": "medium",
            "suggestions": [
                "Keep only last 5 LLM exchanges in context",
                "Summarize old tool outputs instead of including full text",
                "Remove intermediate reasoning steps from context",
                "Implement sliding window for conversation history",
            ],
        })
    
    return recommendations


def _generate_html_report(report_data: dict[str, Any]) -> str:
    """Generate HTML report from report data."""
    template = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgentCoach Analysis Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; margin-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; margin-bottom: 15px; border-bottom: 2px solid #3498db; padding-bottom: 5px; }
        h3 { color: #555; margin-top: 20px; margin-bottom: 10px; }
        .metadata { color: #7f8c8d; font-size: 0.9em; margin-bottom: 20px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .summary-card { background: #ecf0f1; padding: 15px; border-radius: 5px; border-left: 4px solid #3498db; }
        .summary-card h3 { margin: 0 0 10px 0; font-size: 0.9em; color: #7f8c8d; text-transform: uppercase; }
        .summary-card .value { font-size: 2em; font-weight: bold; color: #2c3e50; }
        .quality-score { font-size: 3em; font-weight: bold; }
        .score-good { color: #27ae60; }
        .score-medium { color: #f39c12; }
        .score-poor { color: #e74c3c; }
        .finding { background: #fff; border: 1px solid #ddd; border-left: 4px solid #3498db; padding: 15px; margin: 10px 0; border-radius: 4px; }
        .finding.critical { border-left-color: #e74c3c; }
        .finding.high { border-left-color: #e67e22; }
        .finding.medium { border-left-color: #f39c12; }
        .finding.low { border-left-color: #3498db; }
        .finding.info { border-left-color: #95a5a6; }
        .finding-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .severity-badge { padding: 3px 8px; border-radius: 3px; font-size: 0.85em; font-weight: bold; text-transform: uppercase; }
        .severity-critical { background: #e74c3c; color: white; }
        .severity-high { background: #e67e22; color: white; }
        .severity-medium { background: #f39c12; color: white; }
        .severity-low { background: #3498db; color: white; }
        .severity-info { background: #95a5a6; color: white; }
        .category-badge { background: #ecf0f1; padding: 3px 8px; border-radius: 3px; font-size: 0.85em; margin-left: 5px; }
        .fixes { margin-top: 10px; }
        .fixes ul { margin-left: 20px; }
        .recommendation { background: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 10px 0; border-radius: 4px; }
        .recommendation h4 { color: #2e7d32; margin-bottom: 5px; }
        .recommendation pre { background: #f5f5f5; padding: 10px; border-radius: 3px; overflow-x: auto; font-size: 0.9em; margin-top: 10px; }
        .recommendation ul { margin-left: 20px; margin-top: 10px; }
        details { margin: 10px 0; }
        summary { cursor: pointer; font-weight: bold; padding: 10px; background: #f8f9fa; border-radius: 4px; }
        summary:hover { background: #e9ecef; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 AgentCoach Analysis Report</h1>
        <div class="metadata">
            Generated: {{ metadata.timestamp }}<br>
            Trace ID: {{ metadata.trace_id }}<br>
            Version: {{ metadata.version }}
        </div>

        <h2>📊 Summary</h2>
        <div class="summary">
            <div class="summary-card">
                <h3>Quality Score</h3>
                <div class="value quality-score {% if summary.quality_score >= 80 %}score-good{% elif summary.quality_score >= 50 %}score-medium{% else %}score-poor{% endif %}">
                    {{ summary.quality_score }}%
                </div>
            </div>
            <div class="summary-card">
                <h3>Total Findings</h3>
                <div class="value">{{ summary.total_findings }}</div>
            </div>
            <div class="summary-card">
                <h3>Trace Info</h3>
                <div style="font-size: 0.9em; margin-top: 5px;">
                    Spans: {{ trace_info.span_count }}<br>
                    LLM Calls: {{ trace_info.llm_calls }}<br>
                    Tool Calls: {{ trace_info.tool_calls }}<br>
                    Retrievals: {{ trace_info.retrieval_events }}
                </div>
            </div>
        </div>

        {% if findings %}
        <h2>🔍 Findings</h2>
        {% for finding in findings %}
        <div class="finding {{ finding.severity }}">
            <div class="finding-header">
                <div>
                    <span class="severity-badge severity-{{ finding.severity }}">{{ finding.severity }}</span>
                    <span class="category-badge">{{ finding.category }}</span>
                </div>
            </div>
            <p><strong>{{ finding.message }}</strong></p>
            {% if finding.suggested_fixes %}
            <div class="fixes">
                <strong>Suggested Fixes:</strong>
                <ul>
                    {% for fix in finding.suggested_fixes %}
                    <li>{{ fix }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
            {% if finding.details %}
            <details>
                <summary>Details</summary>
                <pre>{{ finding.details | tojson(indent=2) }}</pre>
            </details>
            {% endif %}
        </div>
        {% endfor %}
        {% endif %}

        {% if recommendations %}
        <h2>💡 Engineering Recommendations</h2>
        {% for rec in recommendations %}
        <div class="recommendation">
            <h4>{{ rec.title }}</h4>
            <p>{{ rec.description }}</p>
            <em>Priority: {{ rec.priority }}</em>
            {% if rec.diff %}
            <pre>{{ rec.diff }}</pre>
            {% endif %}
            {% if rec.code_snippet %}
            <pre>{{ rec.code_snippet }}</pre>
            {% endif %}
            {% if rec.suggestions %}
            <ul>
                {% for suggestion in rec.suggestions %}
                <li>{{ suggestion }}</li>
                {% endfor %}
            </ul>
            {% endif %}
        </div>
        {% endfor %}
        {% endif %}

        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d; font-size: 0.9em; text-align: center;">
            Generated by AgentCoach v{{ metadata.version }}
        </div>
    </div>
</body>
</html>
    """)
    
    return template.render(**report_data)
