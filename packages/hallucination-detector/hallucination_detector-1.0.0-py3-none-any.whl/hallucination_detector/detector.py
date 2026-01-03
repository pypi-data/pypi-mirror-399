"""
Main Hallucination Detector class.

This module contains the primary interface for detecting hallucinations.
"""

import time
import logging
from typing import Optional, List, Dict, Any, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from .types import (
    DetectionResult,
    DetectorConfig,
    HallucinationInstance,
    HallucinationType,
    SeverityLevel,
    ValidationContext,
    Claim,
)
from .analyzers import SemanticAnalyzer, EntityAnalyzer, ClaimExtractor
from .validators import FactValidator, ConsistencyChecker, SourceVerifier

logger = logging.getLogger(__name__)


class HallucinationDetector:
    """
    Production-ready hallucination detection for LLM outputs.
    
    This detector uses multiple strategies to identify hallucinations:
    1. Semantic similarity analysis
    2. Entity verification
    3. Claim extraction and validation
    4. Consistency checking
    5. Source verification
    
    Examples:
        Basic usage:
        >>> detector = HallucinationDetector()
        >>> result = detector.detect(
        ...     response="Paris is the capital of Germany.",
        ...     context="Paris is the capital of France."
        ... )
        >>> print(result.is_hallucination)  # True
        
        With configuration:
        >>> config = DetectorConfig(confidence_threshold=0.8, verbose=True)
        >>> detector = HallucinationDetector(config=config)
        
        Batch processing:
        >>> results = detector.detect_batch([
        ...     {"response": "...", "context": "..."},
        ...     {"response": "...", "context": "..."},
        ... ])
    
    Attributes:
        config: DetectorConfig instance with all settings
        semantic_analyzer: Analyzer for semantic similarity
        entity_analyzer: Analyzer for entity extraction and validation
        claim_extractor: Extractor for claim identification
        fact_validator: Validator for fact checking
        consistency_checker: Checker for internal consistency
    """
    
    def __init__(
        self,
        config: Optional[DetectorConfig] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the HallucinationDetector.
        
        Args:
            config: Optional DetectorConfig instance. If None, uses defaults.
            api_key: Optional API key for external LLM services.
        """
        self.config = config or DetectorConfig()
        self.api_key = api_key
        
        # Initialize components
        self._init_components()
        
        logger.info(f"HallucinationDetector initialized with config: {self.config.to_dict()}")
    
    def _init_components(self) -> None:
        """Initialize all detection components."""
        self.semantic_analyzer = SemanticAnalyzer(
            model_name=self.config.embedding_model,
            use_gpu=self.config.use_gpu,
            cache_embeddings=self.config.cache_embeddings,
        )
        
        self.entity_analyzer = EntityAnalyzer()
        self.claim_extractor = ClaimExtractor(
            min_claim_length=self.config.min_claim_length,
        )
        
        self.fact_validator = FactValidator()
        self.consistency_checker = ConsistencyChecker()
        self.source_verifier = SourceVerifier()
    
    def detect(
        self,
        response: str,
        context: Optional[str] = None,
        sources: Optional[List[str]] = None,
        domain: Optional[str] = None,
        strict: bool = False,
    ) -> DetectionResult:
        """
        Detect hallucinations in an LLM response.
        
        This is the main method for hallucination detection. It analyzes
        the response against provided context and/or sources.
        
        Args:
            response: The LLM-generated response to check.
            context: Optional context/prompt that was given to the LLM.
            sources: Optional list of source documents for verification.
            domain: Optional domain hint (e.g., "medical", "legal").
            strict: If True, uses stricter validation thresholds.
        
        Returns:
            DetectionResult with all findings.
        
        Raises:
            ValueError: If response is empty or invalid.
        
        Examples:
            >>> result = detector.detect(
            ...     response="The patient should take 500mg of aspirin daily.",
            ...     context="Recommended aspirin dose is 75-100mg daily.",
            ...     domain="medical",
            ...     strict=True
            ... )
        """
        if not response or not response.strip():
            raise ValueError("Response cannot be empty")
        
        start_time = time.time()
        
        # Build validation context
        validation_context = None
        if context:
            validation_context = ValidationContext(
                source_text=context,
                source_type="text",
                domain=domain,
                strict_mode=strict,
            )
        
        # Extract claims from response
        claims = self.claim_extractor.extract(response)
        
        if self.config.verbose:
            logger.info(f"Extracted {len(claims)} claims from response")
        
        # Limit claims if needed
        if len(claims) > self.config.max_claims_per_request:
            logger.warning(
                f"Truncating claims from {len(claims)} to {self.config.max_claims_per_request}"
            )
            claims = claims[:self.config.max_claims_per_request]
        
        # Detect hallucinations
        hallucinations = []
        verified_count = 0
        
        for claim in claims:
            claim_result = self._validate_claim(
                claim=claim,
                response=response,
                context=validation_context,
                sources=sources,
            )
            
            if claim_result:
                hallucinations.append(claim_result)
            else:
                verified_count += 1
        
        # Calculate overall confidence
        if hallucinations:
            confidence = sum(h.confidence for h in hallucinations) / len(hallucinations)
        else:
            confidence = 0.0
        
        # Check for consistency issues
        if self.config.enable_semantic_validation:
            consistency_issues = self.consistency_checker.check(response)
            for issue in consistency_issues:
                hallucinations.append(issue)
        
        # Build result
        processing_time = (time.time() - start_time) * 1000
        
        result = DetectionResult(
            is_hallucination=len(hallucinations) > 0,
            confidence=confidence,
            hallucinations=hallucinations,
            total_claims=len(claims),
            verified_claims=verified_count,
            unverified_claims=len(claims) - verified_count,
            processing_time_ms=processing_time,
            model_used=self.config.embedding_model,
            metadata={
                "domain": domain,
                "strict_mode": strict,
                "has_context": context is not None,
                "has_sources": sources is not None and len(sources) > 0,
            },
        )
        
        if self.config.verbose:
            logger.info(f"Detection complete: {result.summary()}")
        
        return result
    
    def _validate_claim(
        self,
        claim: Claim,
        response: str,
        context: Optional[ValidationContext],
        sources: Optional[List[str]],
    ) -> Optional[HallucinationInstance]:
        """
        Validate a single claim against context and sources.
        
        Returns HallucinationInstance if hallucination detected, None otherwise.
        """
        # Entity validation
        if self.config.enable_entity_validation:
            entity_result = self._validate_entities(claim, context)
            if entity_result:
                return entity_result
        
        # Semantic validation
        if self.config.enable_semantic_validation and context:
            semantic_result = self._validate_semantic(claim, context)
            if semantic_result:
                return semantic_result
        
        # Source verification
        if sources:
            source_result = self._validate_against_sources(claim, sources)
            if source_result:
                return source_result
        
        # Fact validation
        fact_result = self.fact_validator.validate(claim)
        if fact_result:
            return fact_result
        
        return None
    
    def _validate_entities(
        self,
        claim: Claim,
        context: Optional[ValidationContext],
    ) -> Optional[HallucinationInstance]:
        """Validate entities in the claim."""
        if not context:
            return None
        
        # Extract entities from claim and context
        claim_entities = self.entity_analyzer.extract(claim.text)
        context_entities = self.entity_analyzer.extract(context.source_text)
        
        # Check for entity mismatches
        for entity in claim_entities:
            if not self.entity_analyzer.verify_against_context(entity, context_entities):
                # Check similarity - might be a variation
                similar = self.entity_analyzer.find_similar(entity, context_entities)
                if similar:
                    return HallucinationInstance(
                        text=entity.text,
                        hallucination_type=HallucinationType.ENTITY_ERROR,
                        severity=SeverityLevel.MEDIUM,
                        confidence=0.8,
                        explanation=f"Entity '{entity.text}' appears incorrect. Did you mean '{similar.text}'?",
                        start_index=claim.start_index,
                        end_index=claim.end_index,
                        suggested_correction=similar.text,
                        source_evidence=context.source_text[:200],
                    )
        
        return None
    
    def _validate_semantic(
        self,
        claim: Claim,
        context: ValidationContext,
    ) -> Optional[HallucinationInstance]:
        """Validate semantic consistency with context."""
        similarity = self.semantic_analyzer.compute_similarity(
            claim.text,
            context.source_text,
        )
        
        threshold = self.config.confidence_threshold
        if context.strict_mode:
            threshold = min(0.9, threshold + 0.1)
        
        if similarity < threshold:
            # Check if it's a contradiction or unsupported
            is_contradiction = self.semantic_analyzer.is_contradiction(
                claim.text,
                context.source_text,
            )
            
            if is_contradiction:
                return HallucinationInstance(
                    text=claim.text,
                    hallucination_type=HallucinationType.CONTRADICTION,
                    severity=SeverityLevel.HIGH,
                    confidence=1.0 - similarity,
                    explanation="This claim contradicts the provided context.",
                    start_index=claim.start_index,
                    end_index=claim.end_index,
                    source_evidence=context.source_text[:200],
                )
            else:
                return HallucinationInstance(
                    text=claim.text,
                    hallucination_type=HallucinationType.UNSUPPORTED_CLAIM,
                    severity=SeverityLevel.MEDIUM,
                    confidence=1.0 - similarity,
                    explanation="This claim is not supported by the provided context.",
                    start_index=claim.start_index,
                    end_index=claim.end_index,
                    source_evidence=context.source_text[:200],
                )
        
        return None
    
    def _validate_against_sources(
        self,
        claim: Claim,
        sources: List[str],
    ) -> Optional[HallucinationInstance]:
        """Validate claim against provided sources."""
        verification = self.source_verifier.verify(claim.text, sources)
        
        if not verification.is_verified:
            return HallucinationInstance(
                text=claim.text,
                hallucination_type=HallucinationType.UNSUPPORTED_CLAIM,
                severity=SeverityLevel.MEDIUM,
                confidence=verification.confidence,
                explanation="This claim could not be verified against provided sources.",
                start_index=claim.start_index,
                end_index=claim.end_index,
            )
        
        return None
    
    def detect_batch(
        self,
        items: List[Dict[str, Any]],
        parallel: bool = True,
    ) -> List[DetectionResult]:
        """
        Detect hallucinations in multiple response-context pairs.
        
        Args:
            items: List of dicts with 'response' and optional 'context', 'sources'.
            parallel: If True, process items in parallel.
        
        Returns:
            List of DetectionResult objects.
        
        Examples:
            >>> results = detector.detect_batch([
            ...     {"response": "...", "context": "..."},
            ...     {"response": "...", "sources": ["...", "..."]},
            ... ])
        """
        if not parallel or len(items) <= 1:
            return [
                self.detect(
                    response=item["response"],
                    context=item.get("context"),
                    sources=item.get("sources"),
                    domain=item.get("domain"),
                    strict=item.get("strict", False),
                )
                for item in items
            ]
        
        results = [None] * len(items)
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_idx = {
                executor.submit(
                    self.detect,
                    response=item["response"],
                    context=item.get("context"),
                    sources=item.get("sources"),
                    domain=item.get("domain"),
                    strict=item.get("strict", False),
                ): idx
                for idx, item in enumerate(items)
            }
            
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    logger.error(f"Error processing item {idx}: {e}")
                    results[idx] = DetectionResult(
                        is_hallucination=False,
                        confidence=0.0,
                        metadata={"error": str(e)},
                    )
        
        return results
    
    def quick_check(self, response: str, context: str) -> bool:
        """
        Quick check if response contains hallucinations.
        
        This is a faster, less detailed check for simple use cases.
        
        Args:
            response: The LLM response to check.
            context: The context/source to check against.
        
        Returns:
            True if hallucination detected, False otherwise.
        
        Examples:
            >>> if detector.quick_check(response, context):
            ...     print("Warning: Potential hallucination!")
        """
        # Fast semantic check
        similarity = self.semantic_analyzer.compute_similarity(response, context)
        return similarity < self.config.confidence_threshold
    
    def get_stats(self) -> Dict[str, Any]:
        """Get detector statistics and performance metrics."""
        return {
            "config": self.config.to_dict(),
            "semantic_analyzer": {
                "model": self.config.embedding_model,
                "cache_size": self.semantic_analyzer.cache_size,
            },
            "claim_extractor": {
                "min_length": self.config.min_claim_length,
            },
        }
    
    def clear_cache(self) -> None:
        """Clear all internal caches."""
        self.semantic_analyzer.clear_cache()
        logger.info("Cache cleared")


class AsyncHallucinationDetector:
    """
    Async version of HallucinationDetector for high-throughput applications.
    
    Examples:
        >>> async_detector = AsyncHallucinationDetector()
        >>> result = await async_detector.detect(response, context)
    """
    
    def __init__(self, config: Optional[DetectorConfig] = None):
        """Initialize async detector."""
        self._sync_detector = HallucinationDetector(config)
    
    async def detect(
        self,
        response: str,
        context: Optional[str] = None,
        sources: Optional[List[str]] = None,
        domain: Optional[str] = None,
        strict: bool = False,
    ) -> DetectionResult:
        """Async version of detect."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._sync_detector.detect(
                response=response,
                context=context,
                sources=sources,
                domain=domain,
                strict=strict,
            ),
        )
    
    async def detect_batch(
        self,
        items: List[Dict[str, Any]],
    ) -> List[DetectionResult]:
        """Async batch detection."""
        import asyncio
        tasks = [
            self.detect(
                response=item["response"],
                context=item.get("context"),
                sources=item.get("sources"),
                domain=item.get("domain"),
                strict=item.get("strict", False),
            )
            for item in items
        ]
        return await asyncio.gather(*tasks)
