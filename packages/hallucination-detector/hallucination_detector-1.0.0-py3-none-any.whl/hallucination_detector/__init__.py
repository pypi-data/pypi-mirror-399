"""
Hallucination Detector - Production-ready hallucination detection for LLMs
===========================================================================

A comprehensive toolkit to detect, measure, and prevent AI hallucinations
in production environments.

Author: Pranay M
License: MIT

Quick Start:
    >>> from hallucination_detector import HallucinationDetector
    >>> detector = HallucinationDetector()
    >>> result = detector.detect(
    ...     response="The Eiffel Tower is located in Berlin.",
    ...     context="The Eiffel Tower is a famous landmark in Paris, France."
    ... )
    >>> print(result.is_hallucination)  # True
    >>> print(result.confidence)  # 0.95
"""

__version__ = "1.0.0"
__author__ = "Pranay M"
__email__ = "pranay@example.com"

from .detector import HallucinationDetector
from .types import DetectionResult, HallucinationType, SeverityLevel
from .validators import FactValidator, ConsistencyChecker, SourceVerifier
from .analyzers import SemanticAnalyzer, EntityAnalyzer, ClaimExtractor
from .reporters import DetectionReport, JSONReporter, HTMLReporter

__all__ = [
    # Core
    "HallucinationDetector",
    # Types
    "DetectionResult",
    "HallucinationType",
    "SeverityLevel",
    # Validators
    "FactValidator",
    "ConsistencyChecker",
    "SourceVerifier",
    # Analyzers
    "SemanticAnalyzer",
    "EntityAnalyzer",
    "ClaimExtractor",
    # Reporters
    "DetectionReport",
    "JSONReporter",
    "HTMLReporter",
]
