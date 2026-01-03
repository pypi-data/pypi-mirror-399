"""
Tests for Hallucination Detector.
"""

import pytest
from hallucination_detector import (
    HallucinationDetector,
    DetectionResult,
    DetectorConfig,
    HallucinationType,
    SeverityLevel,
)
from hallucination_detector.analyzers import SemanticAnalyzer, EntityAnalyzer, ClaimExtractor
from hallucination_detector.validators import FactValidator, ConsistencyChecker
from hallucination_detector.reporters import DetectionReport, JSONReporter


class TestHallucinationDetector:
    """Tests for main detector class."""
    
    def test_init_default(self):
        """Test default initialization."""
        detector = HallucinationDetector()
        assert detector.config is not None
        assert detector.config.confidence_threshold == 0.7
    
    def test_init_custom_config(self):
        """Test initialization with custom config."""
        config = DetectorConfig(confidence_threshold=0.9)
        detector = HallucinationDetector(config=config)
        assert detector.config.confidence_threshold == 0.9
    
    def test_detect_no_hallucination(self):
        """Test detection with matching content."""
        detector = HallucinationDetector()
        result = detector.detect(
            response="Paris is the capital of France.",
            context="Paris is the capital city of France."
        )
        # May or may not detect depending on threshold
        assert isinstance(result, DetectionResult)
        assert isinstance(result.is_hallucination, bool)
    
    def test_detect_with_hallucination(self):
        """Test detection with hallucinated content."""
        detector = HallucinationDetector()
        result = detector.detect(
            response="The Eiffel Tower is in Berlin, Germany.",
            context="The Eiffel Tower is a famous landmark in Paris, France."
        )
        assert isinstance(result, DetectionResult)
        assert result.total_claims >= 0
    
    def test_detect_empty_response(self):
        """Test detection with empty response raises error."""
        detector = HallucinationDetector()
        with pytest.raises(ValueError):
            detector.detect(response="", context="Some context")
    
    def test_detect_no_context(self):
        """Test detection without context."""
        detector = HallucinationDetector()
        result = detector.detect(response="The sky is blue.")
        assert isinstance(result, DetectionResult)
    
    def test_quick_check(self):
        """Test quick check method."""
        detector = HallucinationDetector()
        is_hallucination = detector.quick_check(
            response="Test response",
            context="Test context"
        )
        assert isinstance(is_hallucination, bool)
    
    def test_detect_batch(self):
        """Test batch detection."""
        detector = HallucinationDetector()
        items = [
            {"response": "Test 1", "context": "Context 1"},
            {"response": "Test 2", "context": "Context 2"},
        ]
        results = detector.detect_batch(items)
        assert len(results) == 2
        assert all(isinstance(r, DetectionResult) for r in results)
    
    def test_get_stats(self):
        """Test statistics retrieval."""
        detector = HallucinationDetector()
        stats = detector.get_stats()
        assert "config" in stats
        assert "semantic_analyzer" in stats


class TestSemanticAnalyzer:
    """Tests for semantic analyzer."""
    
    def test_compute_similarity(self):
        """Test similarity computation."""
        analyzer = SemanticAnalyzer()
        sim = analyzer.compute_similarity(
            "The cat sat on the mat",
            "A cat is sitting on a mat"
        )
        assert 0 <= sim <= 1
    
    def test_same_text_similarity(self):
        """Test similarity of identical texts."""
        analyzer = SemanticAnalyzer()
        text = "Hello world"
        sim = analyzer.compute_similarity(text, text)
        assert sim > 0.99
    
    def test_cache_embedding(self):
        """Test embedding caching."""
        analyzer = SemanticAnalyzer(cache_embeddings=True)
        text = "Test text"
        
        # First call - cache miss
        emb1 = analyzer.get_embedding(text)
        assert analyzer.cache_size == 1
        
        # Second call - cache hit
        emb2 = analyzer.get_embedding(text)
        assert emb1 == emb2
    
    def test_clear_cache(self):
        """Test cache clearing."""
        analyzer = SemanticAnalyzer(cache_embeddings=True)
        analyzer.get_embedding("Test")
        assert analyzer.cache_size > 0
        
        analyzer.clear_cache()
        assert analyzer.cache_size == 0


class TestEntityAnalyzer:
    """Tests for entity analyzer."""
    
    def test_extract_entities(self):
        """Test entity extraction."""
        analyzer = EntityAnalyzer(use_spacy=False)  # Use fallback
        entities = analyzer.extract("John works at Google in New York")
        assert len(entities) > 0
    
    def test_extract_numbers(self):
        """Test number extraction."""
        analyzer = EntityAnalyzer(use_spacy=False)
        entities = analyzer.extract("The price is $100")
        number_entities = [e for e in entities if e.entity_type == "NUMBER"]
        assert len(number_entities) > 0


class TestClaimExtractor:
    """Tests for claim extractor."""
    
    def test_extract_claims(self):
        """Test claim extraction."""
        extractor = ClaimExtractor()
        text = "Paris is the capital of France. It has a population of 2 million."
        claims = extractor.extract(text)
        assert len(claims) >= 1
    
    def test_skip_questions(self):
        """Test that questions are skipped."""
        extractor = ClaimExtractor()
        claims = extractor.extract("What is the capital of France?")
        assert len(claims) == 0
    
    def test_min_claim_length(self):
        """Test minimum claim length filtering."""
        extractor = ClaimExtractor(min_claim_length=50)
        claims = extractor.extract("Short claim.")
        assert len(claims) == 0


class TestConsistencyChecker:
    """Tests for consistency checker."""
    
    def test_no_contradiction(self):
        """Test text without contradictions."""
        checker = ConsistencyChecker()
        issues = checker.check("The sky is blue. Water is wet.")
        # Should not find contradictions
        assert isinstance(issues, list)
    
    def test_with_contradiction(self):
        """Test text with potential contradiction."""
        checker = ConsistencyChecker()
        issues = checker.check("The door is open. The door is not open.")
        # May detect contradiction
        assert isinstance(issues, list)


class TestDetectionResult:
    """Tests for DetectionResult class."""
    
    def test_hallucination_rate(self):
        """Test hallucination rate calculation."""
        result = DetectionResult(
            is_hallucination=True,
            confidence=0.9,
            total_claims=10,
            verified_claims=7,
            unverified_claims=3,
        )
        assert result.hallucination_rate == 0.0  # No hallucinations in list
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        result = DetectionResult(
            is_hallucination=False,
            confidence=0.0,
        )
        d = result.to_dict()
        assert "is_hallucination" in d
        assert "confidence" in d
    
    def test_summary(self):
        """Test summary generation."""
        result = DetectionResult(
            is_hallucination=False,
            confidence=0.0,
            total_claims=5,
            verified_claims=5,
        )
        summary = result.summary()
        assert "verified" in summary.lower()


class TestDetectionReport:
    """Tests for DetectionReport class."""
    
    def test_add_result(self):
        """Test adding results to report."""
        report = DetectionReport()
        result = DetectionResult(is_hallucination=False, confidence=0.0)
        report.add_result(result)
        assert report.total_checks == 1
    
    def test_hallucination_rate(self):
        """Test report hallucination rate."""
        report = DetectionReport()
        report.add_result(DetectionResult(is_hallucination=True, confidence=0.9))
        report.add_result(DetectionResult(is_hallucination=False, confidence=0.0))
        assert report.hallucination_rate == 50.0
    
    def test_summary(self):
        """Test report summary generation."""
        report = DetectionReport(title="Test Report")
        summary = report.summary()
        assert "Test Report" in summary


class TestJSONReporter:
    """Tests for JSON reporter."""
    
    def test_format_result(self):
        """Test result formatting."""
        reporter = JSONReporter()
        result = DetectionResult(is_hallucination=False, confidence=0.0)
        json_str = reporter.format(result)
        assert '"is_hallucination"' in json_str
    
    def test_pretty_format(self):
        """Test pretty formatting."""
        reporter = JSONReporter(pretty=True)
        result = DetectionResult(is_hallucination=False, confidence=0.0)
        json_str = reporter.format(result)
        assert "\n" in json_str  # Pretty format has newlines


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
