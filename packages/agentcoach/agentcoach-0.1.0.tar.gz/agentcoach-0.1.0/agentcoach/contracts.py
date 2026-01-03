"""Contract validation utilities."""

import json
from pathlib import Path
from typing import Any, Optional, Union

from jsonschema import Draft7Validator, ValidationError


def load_contract_schema(path: Union[str, Path]) -> dict[str, Any]:
    """Load a JSON schema contract from file.
    
    Args:
        path: Path to JSON schema file
        
    Returns:
        Schema dictionary
    """
    path = Path(path)
    with open(path) as f:
        return json.load(f)


def validate_against_contract(
    data: dict[str, Any],
    schema: dict[str, Any]
) -> tuple[bool, list[str]]:
    """Validate data against a JSON schema contract.
    
    Args:
        data: Data to validate
        schema: JSON schema
        
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    validator = Draft7Validator(schema)
    errors = []
    
    for error in validator.iter_errors(data):
        errors.append(_format_validation_error(error))
    
    return len(errors) == 0, errors


def _format_validation_error(error: ValidationError) -> str:
    """Format a validation error into a readable message."""
    path = ".".join(str(p) for p in error.path) if error.path else "root"
    return f"At '{path}': {error.message}"


def parse_output_as_json(output: str) -> Optional[dict[str, Any]]:
    """Try to parse output as JSON.
    
    Args:
        output: String output to parse
        
    Returns:
        Parsed JSON dict or None if not valid JSON
    """
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        if "```json" in output:
            start = output.find("```json") + 7
            end = output.find("```", start)
            if end > start:
                try:
                    return json.loads(output[start:end].strip())
                except json.JSONDecodeError:
                    pass
        return None
