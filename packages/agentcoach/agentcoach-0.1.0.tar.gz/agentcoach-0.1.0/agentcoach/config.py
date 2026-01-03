"""Configuration management for agentcoach."""

import os
from pathlib import Path
from typing import Any, Union, Optional

import yaml
from dotenv import load_dotenv


def load_config(config_path: Optional[Union[str, Path]] = None) -> dict[str, Any]:
    """Load configuration from file and environment.
    
    Args:
        config_path: Optional path to config YAML file
        
    Returns:
        Configuration dictionary
    """
    # Load environment variables
    load_dotenv()
    
    # Default configuration
    config: dict[str, Any] = {
        "contract_schema": None,
        "policy": None,
        "llm_judge": {
            "enabled": False,
            "provider": None,
        },
        "detectors": {
            "schema": {"enabled": True},
            "grounding": {"enabled": True},
            "tool_use": {"enabled": True},
            "loops": {"enabled": True, "max_repeats": 3},
            "state": {"enabled": True},
            "policy_tone": {"enabled": True},
            "consistency": {"enabled": False},
        },
    }
    
    # Load from file if provided
    if config_path:
        config_path = Path(config_path)
        if config_path.exists():
            with open(config_path) as f:
                file_config = yaml.safe_load(f) or {}
                _merge_config(config, file_config)
    
    return config


def _merge_config(base: dict[str, Any], override: dict[str, Any]) -> None:
    """Recursively merge override config into base config."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _merge_config(base[key], value)
        else:
            base[key] = value


def get_default_config_yaml() -> str:
    """Get default configuration YAML content."""
    return """# AgentCoach Configuration

# Output contract schema (path to JSON schema file)
contract_schema: schemas/default_contract.json

# Policy pack (path to JSON file)
policy: schemas/default_policy.json

# LLM Judge configuration
llm_judge:
  enabled: false
  provider: openai  # openai, anthropic, or sap

# Detector configuration
detectors:
  schema:
    enabled: true
  grounding:
    enabled: true
    require_citations: true
  tool_use:
    enabled: true
  loops:
    enabled: true
    max_repeats: 3
  state:
    enabled: true
  policy_tone:
    enabled: true
  consistency:
    enabled: false
"""


def get_env_example() -> str:
    """Get .env.example content."""
    return """# OpenAI Configuration (optional, for LLM judge)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
# OPENAI_BASE_URL=https://api.openai.com/v1  # Optional: custom endpoint

# Anthropic Configuration (optional, for LLM judge)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# SAP BTP AI Core Configuration (optional, for LLM judge)
AICORE_BASE_URL=https://api.ai.prod.eu-central-1.aws.ml.hana.ondemand.com
AICORE_CLIENT_ID=your_client_id_here
AICORE_CLIENT_SECRET=your_client_secret_here
AICORE_RESOURCE_GROUP=default
AICORE_MODEL=gpt-4
"""
