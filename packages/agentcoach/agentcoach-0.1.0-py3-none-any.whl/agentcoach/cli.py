"""Command-line interface for agentcoach."""

import json
from pathlib import Path
from typing import Optional

import click

from agentcoach import analyze_trace
from agentcoach.canary import generate_canary_suite
from agentcoach.config import get_default_config_yaml, get_env_example, load_config
from agentcoach.contracts import load_contract_schema
from agentcoach.repair import repair_run
from agentcoach.report import generate_report
from agentcoach.trace_ingest import load_trace


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """AgentCoach: Agent quality analysis and repair SDK."""
    pass


@cli.command()
def init() -> None:
    """Initialize agentcoach configuration in current directory."""
    # Create agentcoach.yaml
    config_path = Path("agentcoach.yaml")
    if config_path.exists():
        click.echo("⚠️  agentcoach.yaml already exists")
    else:
        with open(config_path, "w") as f:
            f.write(get_default_config_yaml())
        click.echo(f"✅ Created {config_path}")
    
    # Create .env.example
    env_path = Path(".env.example")
    if not env_path.exists():
        with open(env_path, "w") as f:
            f.write(get_env_example())
        click.echo(f"✅ Created {env_path}")
    
    # Print instrumentation instructions
    click.echo("\n📝 LangGraph Instrumentation Example:")
    click.echo("""
# Add to your LangGraph code:
from langchain_core.tracers import LangChainTracer
import json

tracer = LangChainTracer()
result = graph.invoke(input, config={"callbacks": [tracer]})

# Export trace to JSON
with open("trace.json", "w") as f:
    json.dump(tracer.runs[0].dict(), f)

# Then analyze with:
# agentcoach analyze --trace trace.json --out results/
""")


@cli.command()
@click.option("--trace", required=True, type=click.Path(exists=True), help="Path to trace JSON file")
@click.option("--out", required=True, type=click.Path(), help="Output directory for reports")
@click.option("--config", type=click.Path(exists=True), help="Path to config YAML file")
@click.option("--llm-judge", is_flag=True, help="Enable LLM judge for scoring")
def analyze(trace: str, out: str, config: Optional[str], llm_judge: bool) -> None:
    """Analyze a trace and generate quality reports."""
    click.echo(f"🔍 Analyzing trace: {trace}")
    
    # Load configuration
    cfg = load_config(config)
    
    # Load trace
    try:
        trace_obj = load_trace(trace)
        click.echo(f"✅ Loaded trace with {len(trace_obj.spans)} spans")
    except Exception as e:
        click.echo(f"❌ Failed to load trace: {e}", err=True)
        raise click.Abort()
    
    # Run analysis
    try:
        findings = analyze_trace(trace_obj, cfg)
        click.echo(f"✅ Found {len(findings)} issues")
        
        # Display summary
        by_severity = {}
        for finding in findings:
            sev = finding.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
        
        for sev in ["critical", "high", "medium", "low", "info"]:
            if sev in by_severity:
                click.echo(f"  {sev.upper()}: {by_severity[sev]}")
    
    except Exception as e:
        click.echo(f"❌ Analysis failed: {e}", err=True)
        raise click.Abort()
    
    # Generate reports
    try:
        report_paths = generate_report(trace_obj, findings, out)
        click.echo(f"\n📊 Reports generated:")
        click.echo(f"  JSON: {report_paths['json']}")
        click.echo(f"  HTML: {report_paths['html']}")
    except Exception as e:
        click.echo(f"❌ Report generation failed: {e}", err=True)
        raise click.Abort()
    
    # LLM judge (if enabled)
    if llm_judge:
        click.echo("\n🤖 LLM judge scoring not yet implemented in CLI")
        click.echo("   (Use Python API for LLM judge functionality)")


@cli.command()
@click.option("--trace", required=True, type=click.Path(exists=True), help="Path to trace JSON file")
@click.option("--out", required=True, type=click.Path(), help="Output directory")
@click.option("--llm-provider", type=click.Choice(["openai", "anthropic", "sap"]), help="LLM provider for repair")
@click.option("--config", type=click.Path(exists=True), help="Path to config YAML file")
def repair(trace: str, out: str, llm_provider: Optional[str], config: Optional[str]) -> None:
    """Repair trace output using runtime guard."""
    click.echo(f"🔧 Repairing trace: {trace}")
    
    # Load configuration
    cfg = load_config(config)
    
    # Load trace
    try:
        trace_obj = load_trace(trace)
    except Exception as e:
        click.echo(f"❌ Failed to load trace: {e}", err=True)
        raise click.Abort()
    
    # Load contract schema if configured
    contract_schema = None
    if cfg.get("contract_schema"):
        try:
            contract_schema = load_contract_schema(cfg["contract_schema"])
        except Exception as e:
            click.echo(f"⚠️  Failed to load contract schema: {e}")
    
    # Run repair
    try:
        result = repair_run(
            trace_obj,
            contract_schema=contract_schema,
            llm_provider=llm_provider,
        )
        
        if result.success:
            click.echo(f"✅ Repair successful with {len(result.changes)} change(s)")
            for change in result.changes:
                click.echo(f"  - {change}")
        else:
            click.echo(f"❌ Repair failed: {result.error}")
            raise click.Abort()
    
    except Exception as e:
        click.echo(f"❌ Repair failed: {e}", err=True)
        raise click.Abort()
    
    # Write output
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    result_path = out_dir / "repair_result.json"
    with open(result_path, "w") as f:
        json.dump({
            "original": result.original_output,
            "repaired": result.repaired_output,
            "changes": result.changes,
            "evidence_used": result.evidence_used,
        }, f, indent=2)
    
    click.echo(f"\n📄 Repair result saved to: {result_path}")


@cli.command()
@click.option("--report", required=True, type=click.Path(exists=True), help="Path to report.json")
@click.option("--suite", required=True, type=click.Path(), help="Output directory for canary suite")
def canary(report: str, suite: str) -> None:
    """Generate canary test suite from analysis report."""
    click.echo(f"🧪 Generating canary suite from: {report}")
    
    try:
        paths = generate_canary_suite(report, suite)
        click.echo(f"✅ Canary suite generated:")
        click.echo(f"  Test cases: {paths['cases']}")
        click.echo(f"  Test file: {paths['test_file']}")
        click.echo(f"\n📝 To run tests:")
        click.echo(f"  1. Implement run_agent() in {paths['test_file']}")
        click.echo(f"  2. Run: pytest {paths['test_file']} -v")
    except Exception as e:
        click.echo(f"❌ Failed to generate canary suite: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    cli()
