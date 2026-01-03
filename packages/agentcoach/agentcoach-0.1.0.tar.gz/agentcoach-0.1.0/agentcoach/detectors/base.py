"""Base detector class."""

from abc import ABC, abstractmethod
from typing import Any

from agentcoach.models import Finding, Trace


class Detector(ABC):
    """Base class for all detectors."""
    
    def __init__(self, config: dict[str, Any]):
        """Initialize detector with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
    
    @abstractmethod
    def detect(self, trace: Trace) -> list[Finding]:
        """Detect quality issues in a trace.
        
        Args:
            trace: The trace to analyze
            
        Returns:
            List of findings
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the detector name."""
        pass
