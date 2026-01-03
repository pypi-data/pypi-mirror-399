"""Detector framework for quality analysis."""

from typing import Any

from agentcoach.detectors.base import Detector
from agentcoach.detectors.consistency import ConsistencyDetector
from agentcoach.detectors.grounding import GroundingDetector
from agentcoach.detectors.loops import LoopDetector
from agentcoach.detectors.policy_tone import PolicyToneDetector
from agentcoach.detectors.schema import SchemaDetector
from agentcoach.detectors.state import StateDetector
from agentcoach.detectors.tool_use import ToolUseDetector

__all__ = [
    "Detector",
    "SchemaDetector",
    "GroundingDetector",
    "ToolUseDetector",
    "LoopDetector",
    "StateDetector",
    "PolicyToneDetector",
    "ConsistencyDetector",
    "get_all_detectors",
]


def get_all_detectors(config: dict[str, Any]) -> list[Detector]:
    """Get all enabled detectors based on configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of detector instances
    """
    detectors: list[Detector] = []
    detector_config = config.get("detectors", {})
    
    # Schema detector
    if detector_config.get("schema", {}).get("enabled", True):
        detectors.append(SchemaDetector(config))
    
    # Grounding detector
    if detector_config.get("grounding", {}).get("enabled", True):
        detectors.append(GroundingDetector(config))
    
    # Tool use detector
    if detector_config.get("tool_use", {}).get("enabled", True):
        detectors.append(ToolUseDetector(config))
    
    # Loop detector
    if detector_config.get("loops", {}).get("enabled", True):
        detectors.append(LoopDetector(config))
    
    # State detector
    if detector_config.get("state", {}).get("enabled", True):
        detectors.append(StateDetector(config))
    
    # Policy/tone detector
    if detector_config.get("policy_tone", {}).get("enabled", True):
        detectors.append(PolicyToneDetector(config))
    
    # Consistency detector
    if detector_config.get("consistency", {}).get("enabled", False):
        detectors.append(ConsistencyDetector(config))
    
    return detectors
