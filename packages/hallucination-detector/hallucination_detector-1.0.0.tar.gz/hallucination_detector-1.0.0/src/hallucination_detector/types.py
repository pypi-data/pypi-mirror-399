"""
Type definitions for Hallucination Detector.

This module contains all data classes and enums used throughout the package.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional
from datetime import datetime


class HallucinationType(Enum):
    """Types of hallucinations that can be detected."""
    
    FACTUAL_ERROR = auto()      # Incorrect facts
    ENTITY_ERROR = auto()        # Wrong entities (names, places, etc.)
    TEMPORAL_ERROR = auto()      # Incorrect dates/times
    NUMERIC_ERROR = auto()       # Wrong numbers/statistics
    ATTRIBUTION_ERROR = auto()   # Misattributed quotes/claims
    FABRICATION = auto()         # Completely made-up information
    CONTRADICTION = auto()       # Self-contradicting statements
    CONTEXT_DRIFT = auto()       # Response deviates from context
    UNSUPPORTED_CLAIM = auto()   # Claims without evidence in context
    EXAGGERATION = auto()        # Overstated facts


class SeverityLevel(Enum):
    """Severity levels for detected hallucinations."""
    
    LOW = 1         # Minor inaccuracy, unlikely to cause issues
    MEDIUM = 2      # Noticeable error, may mislead users
    HIGH = 3        # Significant error, likely to cause problems
    CRITICAL = 4    # Severe error, dangerous misinformation


@dataclass
class Claim:
    """Represents an extracted claim from text."""
    
    text: str
    start_index: int
    end_index: int
    claim_type: str = "general"
    entities: List[str] = field(default_factory=list)
    confidence: float = 1.0
    
    def __str__(self) -> str:
        return f"Claim({self.text[:50]}...)" if len(self.text) > 50 else f"Claim({self.text})"


@dataclass
class HallucinationInstance:
    """Represents a single detected hallucination."""
    
    text: str
    hallucination_type: HallucinationType
    severity: SeverityLevel
    confidence: float
    explanation: str
    start_index: int = 0
    end_index: int = 0
    suggested_correction: Optional[str] = None
    source_evidence: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "text": self.text,
            "type": self.hallucination_type.name,
            "severity": self.severity.name,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "start_index": self.start_index,
            "end_index": self.end_index,
            "suggested_correction": self.suggested_correction,
            "source_evidence": self.source_evidence,
        }


@dataclass
class DetectionResult:
    """Complete result of hallucination detection."""
    
    is_hallucination: bool
    confidence: float
    hallucinations: List[HallucinationInstance] = field(default_factory=list)
    total_claims: int = 0
    verified_claims: int = 0
    unverified_claims: int = 0
    processing_time_ms: float = 0.0
    model_used: str = "default"
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def hallucination_rate(self) -> float:
        """Calculate the hallucination rate as a percentage."""
        if self.total_claims == 0:
            return 0.0
        return (len(self.hallucinations) / self.total_claims) * 100
    
    @property
    def severity_breakdown(self) -> Dict[str, int]:
        """Get count of hallucinations by severity."""
        breakdown = {level.name: 0 for level in SeverityLevel}
        for h in self.hallucinations:
            breakdown[h.severity.name] += 1
        return breakdown
    
    @property
    def type_breakdown(self) -> Dict[str, int]:
        """Get count of hallucinations by type."""
        breakdown = {htype.name: 0 for htype in HallucinationType}
        for h in self.hallucinations:
            breakdown[h.hallucination_type.name] += 1
        return breakdown
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "is_hallucination": self.is_hallucination,
            "confidence": self.confidence,
            "hallucinations": [h.to_dict() for h in self.hallucinations],
            "total_claims": self.total_claims,
            "verified_claims": self.verified_claims,
            "unverified_claims": self.unverified_claims,
            "hallucination_rate": self.hallucination_rate,
            "severity_breakdown": self.severity_breakdown,
            "type_breakdown": self.type_breakdown,
            "processing_time_ms": self.processing_time_ms,
            "model_used": self.model_used,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }
    
    def summary(self) -> str:
        """Get a human-readable summary of the detection results."""
        if not self.is_hallucination:
            return f"✅ No hallucinations detected ({self.total_claims} claims verified)"
        
        lines = [
            f"⚠️ {len(self.hallucinations)} hallucination(s) detected",
            f"   Confidence: {self.confidence:.1%}",
            f"   Claims: {self.verified_claims}/{self.total_claims} verified",
            f"   Severity: {self.severity_breakdown}",
        ]
        return "\n".join(lines)


@dataclass
class ValidationContext:
    """Context information for validation."""
    
    source_text: str
    source_type: str = "text"  # text, url, document, database
    source_metadata: Dict[str, Any] = field(default_factory=dict)
    trusted_sources: List[str] = field(default_factory=list)
    domain: Optional[str] = None  # medical, legal, scientific, etc.
    strict_mode: bool = False
    
    def __post_init__(self):
        """Validate context after initialization."""
        if not self.source_text:
            raise ValueError("source_text cannot be empty")


@dataclass
class DetectorConfig:
    """Configuration for the hallucination detector."""
    
    # Detection settings
    confidence_threshold: float = 0.7
    min_claim_length: int = 10
    max_claims_per_request: int = 100
    
    # Model settings
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: Optional[str] = None
    use_gpu: bool = False
    
    # Validation settings
    enable_entity_validation: bool = True
    enable_temporal_validation: bool = True
    enable_numeric_validation: bool = True
    enable_semantic_validation: bool = True
    
    # Performance settings
    batch_size: int = 32
    max_workers: int = 4
    cache_embeddings: bool = True
    
    # Output settings
    include_explanations: bool = True
    include_suggestions: bool = True
    verbose: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "confidence_threshold": self.confidence_threshold,
            "min_claim_length": self.min_claim_length,
            "max_claims_per_request": self.max_claims_per_request,
            "embedding_model": self.embedding_model,
            "llm_model": self.llm_model,
            "use_gpu": self.use_gpu,
            "enable_entity_validation": self.enable_entity_validation,
            "enable_temporal_validation": self.enable_temporal_validation,
            "enable_numeric_validation": self.enable_numeric_validation,
            "enable_semantic_validation": self.enable_semantic_validation,
            "batch_size": self.batch_size,
            "max_workers": self.max_workers,
            "cache_embeddings": self.cache_embeddings,
            "include_explanations": self.include_explanations,
            "include_suggestions": self.include_suggestions,
            "verbose": self.verbose,
        }
