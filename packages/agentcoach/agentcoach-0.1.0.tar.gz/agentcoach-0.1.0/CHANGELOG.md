# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-30

### Added
- Initial release of agentcoach SDK
- Trace ingestion for OpenTelemetry/OpenInference JSON exports
- Seven failure mode detectors:
  - Output contract/schema validation
  - Evidence/grounding verification
  - Tool-use failure detection
  - Loop/planning failure detection
  - State/constraint loss detection
  - Tone/policy compliance
  - Consistency detection (stub)
- JSON and HTML report generation
- Runtime repair loop with tool executor protocol
- Optional LLM judge support (OpenAI, Anthropic, SAP BTP AI Core)
- CLI commands: init, analyze, repair, canary generate
- LangGraph integration with QualityGuardNode
- Canary test suite generation from failures
- Engineering coach recommendations (prompt diffs, retrieval settings, etc.)
