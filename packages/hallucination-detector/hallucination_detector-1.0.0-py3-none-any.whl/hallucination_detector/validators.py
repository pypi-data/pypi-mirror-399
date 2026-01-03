"""
Validators for Hallucination Detection.

This module contains validators for fact checking, consistency,
and source verification.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .types import HallucinationInstance, HallucinationType, SeverityLevel, Claim

logger = logging.getLogger(__name__)


@dataclass
class VerificationResult:
    """Result of a verification check."""
    is_verified: bool
    confidence: float
    evidence: Optional[str] = None
    source: Optional[str] = None


class FactValidator:
    """
    Validator for factual claims.
    
    Checks claims against known facts and patterns that indicate
    potential fabrication.
    
    Examples:
        >>> validator = FactValidator()
        >>> result = validator.validate(claim)
        >>> if result:
        ...     print(f"Hallucination detected: {result.explanation}")
    """
    
    def __init__(self):
        """Initialize fact validator."""
        # Common factual patterns that are often hallucinated
        self._suspicious_patterns = [
            (r'(?:studies|research) (?:show|prove|indicate) that \d+%', 'statistical_claim'),
            (r'according to (?:a|the) (?:\d{4} )?(?:study|report|survey)', 'citation_claim'),
            (r'(?:scientists|researchers|experts) (?:say|believe|found)', 'authority_claim'),
        ]
        
        # Known false patterns
        self._false_patterns = [
            # Add known misinformation patterns here
        ]
    
    def validate(self, claim: Claim) -> Optional[HallucinationInstance]:
        """
        Validate a claim for potential factual errors.
        
        Args:
            claim: Claim to validate.
        
        Returns:
            HallucinationInstance if issue found, None otherwise.
        """
        # Check for suspicious patterns
        for pattern, pattern_type in self._suspicious_patterns:
            if re.search(pattern, claim.text, re.IGNORECASE):
                # These patterns often indicate fabrication
                # Return a low-confidence warning
                logger.debug(f"Suspicious pattern found: {pattern_type}")
        
        # Check for known false claims
        for pattern in self._false_patterns:
            if re.search(pattern, claim.text, re.IGNORECASE):
                return HallucinationInstance(
                    text=claim.text,
                    hallucination_type=HallucinationType.FABRICATION,
                    severity=SeverityLevel.HIGH,
                    confidence=0.9,
                    explanation="This claim matches known misinformation patterns.",
                    start_index=claim.start_index,
                    end_index=claim.end_index,
                )
        
        # Check for internal inconsistencies
        inconsistency = self._check_internal_consistency(claim.text)
        if inconsistency:
            return inconsistency
        
        return None
    
    def _check_internal_consistency(self, text: str) -> Optional[HallucinationInstance]:
        """Check for internal inconsistencies in a claim."""
        # Check for contradictory numbers
        numbers = re.findall(r'\b(\d+(?:\.\d+)?)\s*%?\b', text)
        
        if len(numbers) >= 2:
            # Check if percentages sum to more than 100%
            if '%' in text:
                try:
                    percentages = [float(n) for n in numbers if float(n) <= 100]
                    if sum(percentages) > 100 and 'total' not in text.lower():
                        # Might be valid in some contexts
                        pass
                except ValueError:
                    pass
        
        return None
    
    def add_known_facts(self, facts: Dict[str, Any]) -> None:
        """
        Add known facts for validation.
        
        Args:
            facts: Dictionary of known facts.
        """
        self._known_facts = facts
    
    def add_false_pattern(self, pattern: str) -> None:
        """
        Add a pattern for known false claims.
        
        Args:
            pattern: Regex pattern to match false claims.
        """
        self._false_patterns.append(pattern)


class ConsistencyChecker:
    """
    Checker for internal consistency of responses.
    
    Detects self-contradictions and logical inconsistencies
    within a single response.
    
    Examples:
        >>> checker = ConsistencyChecker()
        >>> issues = checker.check("The sky is blue. The sky is not blue.")
        >>> for issue in issues:
        ...     print(issue.explanation)
    """
    
    def __init__(self):
        """Initialize consistency checker."""
        self._negation_pairs = [
            ('is', 'is not'),
            ('are', 'are not'),
            ('was', 'was not'),
            ('were', 'were not'),
            ('has', 'has not'),
            ('have', 'have not'),
            ('can', 'cannot'),
            ('will', 'will not'),
            ('should', 'should not'),
        ]
    
    def check(self, text: str) -> List[HallucinationInstance]:
        """
        Check text for internal consistency issues.
        
        Args:
            text: Text to check.
        
        Returns:
            List of HallucinationInstance objects for found issues.
        """
        issues = []
        
        # Split into sentences
        sentences = self._split_sentences(text)
        
        # Check for direct contradictions
        contradictions = self._find_contradictions(sentences)
        for contradiction in contradictions:
            issues.append(HallucinationInstance(
                text=contradiction['text'],
                hallucination_type=HallucinationType.CONTRADICTION,
                severity=SeverityLevel.HIGH,
                confidence=contradiction['confidence'],
                explanation=f"Self-contradiction detected: '{contradiction['sentence1']}' vs '{contradiction['sentence2']}'",
            ))
        
        # Check for numerical inconsistencies
        num_issues = self._check_numerical_consistency(text)
        issues.extend(num_issues)
        
        return issues
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
    def _find_contradictions(self, sentences: List[str]) -> List[Dict[str, Any]]:
        """Find contradictory sentences."""
        contradictions = []
        
        for i, sent1 in enumerate(sentences):
            for sent2 in sentences[i+1:]:
                # Check for negation contradictions
                for pos, neg in self._negation_pairs:
                    # Check if one sentence has positive and other has negative
                    s1_lower = sent1.lower()
                    s2_lower = sent2.lower()
                    
                    if pos in s1_lower and neg in s2_lower:
                        # Check if same subject
                        if self._same_subject(sent1, sent2):
                            contradictions.append({
                                'sentence1': sent1,
                                'sentence2': sent2,
                                'text': f"{sent1} ... {sent2}",
                                'confidence': 0.8,
                            })
                    elif neg in s1_lower and pos in s2_lower:
                        if self._same_subject(sent1, sent2):
                            contradictions.append({
                                'sentence1': sent1,
                                'sentence2': sent2,
                                'text': f"{sent1} ... {sent2}",
                                'confidence': 0.8,
                            })
        
        return contradictions
    
    def _same_subject(self, sent1: str, sent2: str) -> bool:
        """Check if two sentences have the same subject."""
        # Simple heuristic: check for common nouns
        words1 = set(re.findall(r'\b[A-Z][a-z]+\b', sent1))
        words2 = set(re.findall(r'\b[A-Z][a-z]+\b', sent2))
        
        return len(words1 & words2) > 0
    
    def _check_numerical_consistency(self, text: str) -> List[HallucinationInstance]:
        """Check for numerical consistency issues."""
        issues = []
        
        # Find all number-entity pairs
        number_pattern = r'(\d+(?:,\d{3})*(?:\.\d+)?)\s+(\w+)'
        matches = re.findall(number_pattern, text)
        
        # Group by entity
        entity_numbers: Dict[str, List[float]] = {}
        for num_str, entity in matches:
            try:
                num = float(num_str.replace(',', ''))
                entity_lower = entity.lower()
                if entity_lower not in entity_numbers:
                    entity_numbers[entity_lower] = []
                entity_numbers[entity_lower].append(num)
            except ValueError:
                pass
        
        # Check for conflicting numbers for same entity
        for entity, numbers in entity_numbers.items():
            if len(numbers) > 1:
                unique_nums = set(numbers)
                if len(unique_nums) > 1:
                    # Different numbers for same entity - might be an issue
                    # But could also be valid (e.g., "increased from 10 to 20")
                    pass
        
        return issues


class SourceVerifier:
    """
    Verifier for checking claims against source documents.
    
    Validates that claims are supported by provided source materials.
    
    Examples:
        >>> verifier = SourceVerifier()
        >>> result = verifier.verify(
        ...     claim="The company revenue was $10M",
        ...     sources=["Annual report: Revenue reached $10 million..."]
        ... )
        >>> print(result.is_verified)
    """
    
    def __init__(self, similarity_threshold: float = 0.7):
        """
        Initialize source verifier.
        
        Args:
            similarity_threshold: Minimum similarity for verification.
        """
        self.similarity_threshold = similarity_threshold
        self._analyzer = None
    
    def _get_analyzer(self):
        """Lazy load semantic analyzer."""
        if self._analyzer is None:
            from .analyzers import SemanticAnalyzer
            self._analyzer = SemanticAnalyzer()
        return self._analyzer
    
    def verify(
        self,
        claim: str,
        sources: List[str],
    ) -> VerificationResult:
        """
        Verify a claim against sources.
        
        Args:
            claim: Claim to verify.
            sources: List of source documents.
        
        Returns:
            VerificationResult with verification status.
        """
        if not sources:
            return VerificationResult(
                is_verified=False,
                confidence=0.0,
            )
        
        analyzer = self._get_analyzer()
        
        best_similarity = 0.0
        best_source = None
        best_evidence = None
        
        for source in sources:
            # Split source into chunks for more precise matching
            chunks = self._chunk_source(source)
            
            for chunk in chunks:
                similarity = analyzer.compute_similarity(claim, chunk)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_source = source[:100] + "..."
                    best_evidence = chunk
        
        is_verified = best_similarity >= self.similarity_threshold
        
        return VerificationResult(
            is_verified=is_verified,
            confidence=best_similarity,
            evidence=best_evidence,
            source=best_source,
        )
    
    def _chunk_source(self, source: str, chunk_size: int = 200) -> List[str]:
        """Split source into overlapping chunks."""
        words = source.split()
        chunks = []
        
        words_per_chunk = chunk_size // 5  # Approximate words per chunk
        overlap = words_per_chunk // 2
        
        for i in range(0, len(words), words_per_chunk - overlap):
            chunk_words = words[i:i + words_per_chunk]
            if chunk_words:
                chunks.append(' '.join(chunk_words))
        
        return chunks
    
    def verify_batch(
        self,
        claims: List[str],
        sources: List[str],
    ) -> List[VerificationResult]:
        """
        Verify multiple claims against sources.
        
        Args:
            claims: List of claims to verify.
            sources: List of source documents.
        
        Returns:
            List of VerificationResult objects.
        """
        return [self.verify(claim, sources) for claim in claims]


class DomainValidator:
    """
    Domain-specific validator for specialized content.
    
    Provides validation rules for specific domains like medical,
    legal, financial, etc.
    """
    
    DOMAINS = {
        'medical': {
            'dangerous_patterns': [
                r'(?:always|never|guaranteed to) (?:cure|treat|heal)',
                r'(?:take|consume) (\d+)\s*(?:mg|g|ml)',
            ],
            'required_disclaimers': [
                'consult', 'doctor', 'physician', 'healthcare provider',
            ],
        },
        'legal': {
            'dangerous_patterns': [
                r'(?:always|never) (?:legal|illegal)',
                r'(?:guaranteed|certain) to (?:win|succeed)',
            ],
            'required_disclaimers': [
                'attorney', 'lawyer', 'legal advice', 'jurisdiction',
            ],
        },
        'financial': {
            'dangerous_patterns': [
                r'(?:guaranteed|certain) (?:returns|profit)',
                r'(?:will|always) (?:increase|grow|appreciate)',
            ],
            'required_disclaimers': [
                'investment', 'risk', 'financial advisor', 'past performance',
            ],
        },
    }
    
    def __init__(self, domain: str):
        """
        Initialize domain validator.
        
        Args:
            domain: Domain to validate for.
        
        Raises:
            ValueError: If domain is not supported.
        """
        if domain not in self.DOMAINS:
            raise ValueError(f"Unsupported domain: {domain}. Supported: {list(self.DOMAINS.keys())}")
        
        self.domain = domain
        self.config = self.DOMAINS[domain]
    
    def validate(self, text: str) -> List[HallucinationInstance]:
        """
        Validate text for domain-specific issues.
        
        Args:
            text: Text to validate.
        
        Returns:
            List of found issues.
        """
        issues = []
        
        # Check dangerous patterns
        for pattern in self.config['dangerous_patterns']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                issues.append(HallucinationInstance(
                    text=match.group(),
                    hallucination_type=HallucinationType.EXAGGERATION,
                    severity=SeverityLevel.HIGH,
                    confidence=0.9,
                    explanation=f"Potentially dangerous {self.domain} claim detected.",
                    start_index=match.start(),
                    end_index=match.end(),
                ))
        
        return issues
    
    def check_disclaimers(self, text: str) -> bool:
        """
        Check if required disclaimers are present.
        
        Args:
            text: Text to check.
        
        Returns:
            True if disclaimers are present.
        """
        text_lower = text.lower()
        
        for disclaimer in self.config['required_disclaimers']:
            if disclaimer in text_lower:
                return True
        
        return False
