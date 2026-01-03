"""
Analyzers for Hallucination Detection.

This module contains analyzers for semantic similarity, entity extraction,
and claim extraction.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Represents an extracted entity."""
    text: str
    entity_type: str  # PERSON, ORG, GPE, DATE, NUMBER, etc.
    start: int = 0
    end: int = 0
    confidence: float = 1.0


class SemanticAnalyzer:
    """
    Analyzer for semantic similarity and contradiction detection.
    
    Uses sentence embeddings to compute semantic similarity between texts.
    Supports caching for improved performance.
    
    Examples:
        >>> analyzer = SemanticAnalyzer()
        >>> similarity = analyzer.compute_similarity(
        ...     "The sky is blue.",
        ...     "The sky has a blue color."
        ... )
        >>> print(similarity)  # ~0.9
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        use_gpu: bool = False,
        cache_embeddings: bool = True,
    ):
        """
        Initialize the semantic analyzer.
        
        Args:
            model_name: Name of the sentence-transformer model.
            use_gpu: Whether to use GPU acceleration.
            cache_embeddings: Whether to cache computed embeddings.
        """
        self.model_name = model_name
        self.use_gpu = use_gpu
        self._cache_embeddings = cache_embeddings
        self._embedding_cache: Dict[str, List[float]] = {}
        self._model = None
    
    def _load_model(self):
        """Lazy load the model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                device = "cuda" if self.use_gpu else "cpu"
                self._model = SentenceTransformer(self.model_name, device=device)
                logger.info(f"Loaded model {self.model_name} on {device}")
            except ImportError:
                logger.warning(
                    "sentence-transformers not installed. "
                    "Using fallback similarity method."
                )
                self._model = "fallback"
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for text.
        
        Args:
            text: Text to embed.
        
        Returns:
            List of floats representing the embedding.
        """
        if self._cache_embeddings and text in self._embedding_cache:
            return self._embedding_cache[text]
        
        self._load_model()
        
        if self._model == "fallback":
            # Simple fallback using word frequency
            embedding = self._fallback_embedding(text)
        else:
            embedding = self._model.encode(text).tolist()
        
        if self._cache_embeddings:
            self._embedding_cache[text] = embedding
        
        return embedding
    
    def _fallback_embedding(self, text: str) -> List[float]:
        """Simple fallback embedding using character/word features."""
        words = text.lower().split()
        # Create a simple 100-dim embedding
        embedding = [0.0] * 100
        for i, word in enumerate(words[:100]):
            for j, char in enumerate(word[:10]):
                idx = (i * 10 + j) % 100
                embedding[idx] += ord(char) / 1000.0
        
        # Normalize
        magnitude = sum(x**2 for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute semantic similarity between two texts.
        
        Args:
            text1: First text.
            text2: Second text.
        
        Returns:
            Similarity score between 0 and 1.
        
        Examples:
            >>> sim = analyzer.compute_similarity("Hello world", "Hi there world")
            >>> print(f"{sim:.2f}")  # ~0.7
        """
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        
        return self._cosine_similarity(emb1, emb2)
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def is_contradiction(self, text1: str, text2: str) -> bool:
        """
        Check if two texts contradict each other.
        
        Args:
            text1: First text.
            text2: Second text.
        
        Returns:
            True if texts contradict each other.
        """
        # Simple contradiction detection using negation patterns
        negation_words = {"not", "no", "never", "neither", "nobody", "nothing", "nowhere"}
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Check for negation asymmetry
        neg1 = bool(words1 & negation_words)
        neg2 = bool(words2 & negation_words)
        
        # High similarity but different negation = contradiction
        similarity = self.compute_similarity(text1, text2)
        
        if neg1 != neg2 and similarity > 0.5:
            return True
        
        return False
    
    def find_most_similar(
        self,
        query: str,
        candidates: List[str],
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Find most similar texts from candidates.
        
        Args:
            query: Query text.
            candidates: List of candidate texts.
            top_k: Number of top results to return.
        
        Returns:
            List of (text, similarity) tuples sorted by similarity.
        """
        results = []
        query_emb = self.get_embedding(query)
        
        for candidate in candidates:
            cand_emb = self.get_embedding(candidate)
            sim = self._cosine_similarity(query_emb, cand_emb)
            results.append((candidate, sim))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    @property
    def cache_size(self) -> int:
        """Get current cache size."""
        return len(self._embedding_cache)
    
    def clear_cache(self) -> None:
        """Clear embedding cache."""
        self._embedding_cache.clear()


class EntityAnalyzer:
    """
    Analyzer for entity extraction and validation.
    
    Extracts named entities (people, organizations, locations, etc.)
    and validates them against context.
    
    Examples:
        >>> analyzer = EntityAnalyzer()
        >>> entities = analyzer.extract("John works at Google in New York.")
        >>> for e in entities:
        ...     print(f"{e.text}: {e.entity_type}")
        # John: PERSON
        # Google: ORG
        # New York: GPE
    """
    
    def __init__(self, use_spacy: bool = True):
        """
        Initialize entity analyzer.
        
        Args:
            use_spacy: Whether to use spaCy for NER (falls back to regex).
        """
        self.use_spacy = use_spacy
        self._nlp = None
    
    def _load_nlp(self):
        """Lazy load spaCy model."""
        if self._nlp is None and self.use_spacy:
            try:
                import spacy
                try:
                    self._nlp = spacy.load("en_core_web_sm")
                except OSError:
                    logger.warning("spaCy model not found. Using fallback.")
                    self._nlp = "fallback"
            except ImportError:
                logger.warning("spaCy not installed. Using fallback.")
                self._nlp = "fallback"
    
    def extract(self, text: str) -> List[Entity]:
        """
        Extract entities from text.
        
        Args:
            text: Text to extract entities from.
        
        Returns:
            List of Entity objects.
        """
        self._load_nlp()
        
        if self._nlp and self._nlp != "fallback":
            return self._extract_with_spacy(text)
        else:
            return self._extract_with_regex(text)
    
    def _extract_with_spacy(self, text: str) -> List[Entity]:
        """Extract entities using spaCy."""
        doc = self._nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append(Entity(
                text=ent.text,
                entity_type=ent.label_,
                start=ent.start_char,
                end=ent.end_char,
            ))
        
        return entities
    
    def _extract_with_regex(self, text: str) -> List[Entity]:
        """Extract entities using regex patterns (fallback)."""
        entities = []
        
        # Capitalized words (potential names/places)
        for match in re.finditer(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text):
            entities.append(Entity(
                text=match.group(),
                entity_type="PROPER_NOUN",
                start=match.start(),
                end=match.end(),
            ))
        
        # Numbers
        for match in re.finditer(r'\b\d+(?:\.\d+)?(?:%|kg|km|m|cm|mm|lb|oz)?\b', text):
            entities.append(Entity(
                text=match.group(),
                entity_type="NUMBER",
                start=match.start(),
                end=match.end(),
            ))
        
        # Dates
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
            r'\b\d{1,2}-\d{1,2}-\d{2,4}\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
        ]
        for pattern in date_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(Entity(
                    text=match.group(),
                    entity_type="DATE",
                    start=match.start(),
                    end=match.end(),
                ))
        
        return entities
    
    def verify_against_context(
        self,
        entity: Entity,
        context_entities: List[Entity],
    ) -> bool:
        """
        Verify if entity exists in context entities.
        
        Args:
            entity: Entity to verify.
            context_entities: List of entities from context.
        
        Returns:
            True if entity is found in context.
        """
        entity_text_lower = entity.text.lower()
        
        for ctx_entity in context_entities:
            if ctx_entity.text.lower() == entity_text_lower:
                return True
        
        return False
    
    def find_similar(
        self,
        entity: Entity,
        context_entities: List[Entity],
        threshold: float = 0.8,
    ) -> Optional[Entity]:
        """
        Find similar entity in context.
        
        Args:
            entity: Entity to find similar match for.
            context_entities: List of entities from context.
            threshold: Minimum similarity threshold.
        
        Returns:
            Most similar entity if found, None otherwise.
        """
        entity_text = entity.text.lower()
        best_match = None
        best_score = 0.0
        
        for ctx_entity in context_entities:
            ctx_text = ctx_entity.text.lower()
            
            # Simple character-level similarity
            score = self._string_similarity(entity_text, ctx_text)
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = ctx_entity
        
        return best_match
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """Compute string similarity using Levenshtein ratio."""
        if s1 == s2:
            return 1.0
        
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 0.0
        
        # Simple character overlap
        set1, set2 = set(s1), set(s2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0


class ClaimExtractor:
    """
    Extractor for identifying claims in text.
    
    Breaks down text into individual verifiable claims that can
    be checked for hallucinations.
    
    Examples:
        >>> extractor = ClaimExtractor()
        >>> claims = extractor.extract(
        ...     "Paris is the capital of France. It has a population of 2 million."
        ... )
        >>> for claim in claims:
        ...     print(claim.text)
    """
    
    def __init__(self, min_claim_length: int = 10):
        """
        Initialize claim extractor.
        
        Args:
            min_claim_length: Minimum character length for a claim.
        """
        self.min_claim_length = min_claim_length
    
    def extract(self, text: str) -> List["Claim"]:
        """
        Extract claims from text.
        
        Args:
            text: Text to extract claims from.
        
        Returns:
            List of Claim objects.
        """
        from .types import Claim
        
        claims = []
        
        # Split by sentence
        sentences = self._split_sentences(text)
        
        current_pos = 0
        for sentence in sentences:
            sentence = sentence.strip()
            
            if len(sentence) < self.min_claim_length:
                current_pos += len(sentence) + 1
                continue
            
            # Skip questions and exclamations (usually not claims)
            if sentence.endswith('?'):
                current_pos += len(sentence) + 1
                continue
            
            # Extract sub-claims if sentence has multiple parts
            sub_claims = self._extract_sub_claims(sentence)
            
            start_idx = text.find(sentence, current_pos)
            if start_idx == -1:
                start_idx = current_pos
            
            for sub_claim in sub_claims:
                if len(sub_claim) >= self.min_claim_length:
                    claim_start = text.find(sub_claim, start_idx)
                    claims.append(Claim(
                        text=sub_claim,
                        start_index=claim_start if claim_start >= 0 else start_idx,
                        end_index=claim_start + len(sub_claim) if claim_start >= 0 else start_idx + len(sub_claim),
                        claim_type=self._classify_claim(sub_claim),
                    ))
            
            current_pos = start_idx + len(sentence)
        
        return claims
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s for s in sentences if s.strip()]
    
    def _extract_sub_claims(self, sentence: str) -> List[str]:
        """Extract sub-claims from a compound sentence."""
        # Split on conjunctions
        parts = re.split(r'\s*(?:,\s*(?:and|but|or|however|therefore|thus))\s*', sentence)
        
        # Also split on semicolons
        all_parts = []
        for part in parts:
            all_parts.extend(part.split(';'))
        
        return [p.strip() for p in all_parts if p.strip()]
    
    def _classify_claim(self, claim: str) -> str:
        """Classify the type of claim."""
        claim_lower = claim.lower()
        
        # Numerical claim
        if re.search(r'\d+', claim):
            if any(word in claim_lower for word in ['percent', '%', 'ratio', 'rate']):
                return "statistical"
            if re.search(r'\b\d{4}\b', claim):
                return "temporal"
            return "numerical"
        
        # Definition
        if ' is ' in claim_lower or ' are ' in claim_lower:
            if any(word in claim_lower for word in ['defined as', 'known as', 'called']):
                return "definition"
            return "factual"
        
        # Causal
        if any(word in claim_lower for word in ['because', 'cause', 'result', 'lead to', 'due to']):
            return "causal"
        
        return "general"
