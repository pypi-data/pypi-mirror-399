"""
Similarity Calculator Module

This module provides comprehensive similarity calculation capabilities for the
Semantica framework, computing semantic similarity between entities using multiple
metrics including string similarity, property similarity, relationship similarity,
and embedding similarity.

Algorithms Used:
    - Blocking Strategy: Prefix-based entity grouping to reduce O(n²) comparisons
    - Pre-processing: Vectorized preparation of lowercase names and relationship sets
    - Short-circuiting: Early exit for dissimilar pairs based on name similarity
    - Levenshtein Distance: Dynamic programming algorithm for edit distance calculation
    - Jaro Similarity: Character-based similarity with match window algorithm
    - Jaro-Winkler Similarity: Jaro with prefix bonus (up to 4 characters, 0.1 weight)
    - Cosine Similarity: Vector dot product divided by magnitudes for embeddings
    - Jaccard Similarity: Intersection over union for relationship sets
    - Property Matching: Weighted comparison of property values with type-aware matching
    - Multi-factor Aggregation: Weighted sum of similarity components with normalization

Key Features:
    - Blocking strategy and short-circuiting for high-performance large-scale processing
    - Multi-factor similarity calculation (string, property, relationship, embedding)
    - Multiple string similarity algorithms (Levenshtein, Jaro-Winkler, cosine)
    - Weighted aggregation of similarity components with automatic normalization
    - Batch similarity calculation for efficiency (O(n²) optimized)
    - Configurable similarity thresholds and component weights
    - Support for exact matching, fuzzy matching, and semantic matching

Main Classes:
    - SimilarityCalculator: Main similarity calculation engine
    - SimilarityResult: Similarity calculation result with component scores

Example Usage:
    >>> from semantica.deduplication import SimilarityCalculator
    >>> calculator = SimilarityCalculator(
    ...     string_weight=0.4,
    ...     property_weight=0.3,
    ...     embedding_weight=0.3
    ... )
    >>> similarity = calculator.calculate_similarity(entity1, entity2)
    >>> batch_results = calculator.batch_calculate_similarity(entities, threshold=0.7)
    >>> 
    >>> # String similarity methods
    >>> lev_score = calculator.calculate_string_similarity("Apple", "Apple Inc.", method="levenshtein")
    >>> jaro_score = calculator.calculate_string_similarity("Apple", "Apple Inc.", method="jaro_winkler")

Author: Semantica Contributors
License: MIT
"""

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from ..utils.exceptions import ProcessingError
from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker


@dataclass
class SimilarityResult:
    """Similarity calculation result."""

    score: float
    method: str
    components: Dict[str, float] = None
    metadata: Dict[str, Any] = None


class SimilarityCalculator:
    """
    Similarity calculation engine for entity comparison.

    This class provides comprehensive similarity calculation using multiple factors:
    string similarity, property similarity, relationship similarity, and embedding
    similarity. Results are aggregated using configurable weights.

    Similarity Components:
        - String similarity: Name/identifier comparison using various algorithms
        - Property similarity: Comparison of entity properties
        - Relationship similarity: Comparison of entity relationships
        - Embedding similarity: Semantic similarity using vector embeddings

    Example Usage:
        >>> calculator = SimilarityCalculator(
        ...     string_weight=0.4,
        ...     property_weight=0.3,
        ...     embedding_weight=0.3
        ... )
        >>> result = calculator.calculate_similarity(entity1, entity2)
        >>> print(f"Similarity: {result.score:.2f}")
    """

    def __init__(
        self,
        embedding_weight: float = 0.0,
        string_weight: float = 0.6,
        property_weight: float = 0.2,
        relationship_weight: float = 0.2,
        similarity_threshold: float = 0.7,
        config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        Initialize similarity calculator.

        Sets up the calculator with configurable weights for different similarity
        components. Weights are normalized automatically if they don't sum to 1.0.

        Args:
            embedding_weight: Weight for embedding similarity (default: 0.4)
            string_weight: Weight for string similarity (default: 0.3)
            property_weight: Weight for property similarity (default: 0.2)
            relationship_weight: Weight for relationship similarity (default: 0.1)
            similarity_threshold: Default similarity threshold for filtering (default: 0.7)
            config: Configuration dictionary (merged with kwargs)
            **kwargs: Additional configuration options
        """
        self.logger = get_logger("similarity_calculator")

        # Merge configuration
        self.config = config or {}
        self.config.update(kwargs)

        # Component weights (used for weighted aggregation)
        self.embedding_weight = embedding_weight
        self.string_weight = string_weight
        self.property_weight = property_weight
        self.relationship_weight = relationship_weight
        self.similarity_threshold = similarity_threshold

        # Validate weights sum to approximately 1.0
        total_weight = (
            self.embedding_weight
            + self.string_weight
            + self.property_weight
            + self.relationship_weight
        )
        if abs(total_weight - 1.0) > 0.01:
            self.logger.debug(
                f"Weights sum to {total_weight:.2f}, will be normalized during calculation"
            )

        # Initialize progress tracker and ensure it's enabled
        self.progress_tracker = get_progress_tracker()
        if not self.progress_tracker.enabled:
            self.progress_tracker.enabled = True

        self.logger.debug("Similarity calculator initialized")

    def calculate_similarity(
        self, entity1: Dict[str, Any], entity2: Dict[str, Any], track: bool = True, **options
    ) -> SimilarityResult:
        """
        Calculate overall similarity between two entities.

        This method computes a comprehensive similarity score by combining multiple
        similarity factors: string similarity, property similarity, relationship
        similarity, and embedding similarity (if available). Results are aggregated
        using configurable weights.

        Args:
            entity1: First entity dictionary
            entity2: Second entity dictionary
            track: Whether to track progress for this individual calculation (default: True)
            **options: Additional calculation options

        Returns:
            SimilarityResult object
        """
        tracking_id = None
        if track:
            # Track similarity calculation
            tracking_id = self.progress_tracker.start_tracking(
                file=None,
                module="deduplication",
                submodule="SimilarityCalculator",
                message="Calculating similarity between entities",
            )

        try:
            components = {}

            # String similarity (usually the most important and fastest)
            if tracking_id:
                self.progress_tracker.update_tracking(
                    tracking_id, message="Calculating string similarity..."
                )
            
            # Use pre-calculated lowercase name if available
            name1 = entity1.get("_lower_name")
            if name1 is None:
                name1 = entity1.get("name") or entity1.get("text") or ""
            
            name2 = entity2.get("_lower_name")
            if name2 is None:
                name2 = entity2.get("name") or entity2.get("text") or ""
                
            string_score = self.calculate_string_similarity(name1, name2)
            components["string"] = string_score

            # Short-circuit if string similarity is too low and weight is high
            # If string similarity is 0 and it accounts for 60% of score,
            # max possible score is 0.4, which is below most thresholds.
            if self.string_weight > 0.5 and string_score < 0.3 and not ("embedding" in entity1 and "embedding" in entity2):
                # Only short-circuit if no embeddings (which might provide semantic similarity)
                # and string similarity is very low.
                overall_score = string_score * self.string_weight # Rough estimate
                if overall_score < (options.get("threshold") or self.similarity_threshold) * 0.5:
                    return SimilarityResult(score=overall_score, method="short_circuit", components=components)

            # Property similarity
            if tracking_id:
                self.progress_tracker.update_tracking(
                    tracking_id, message="Calculating property similarity..."
                )
            property_score = self.calculate_property_similarity(entity1, entity2)
            components["property"] = property_score

            # Relationship similarity
            if tracking_id:
                self.progress_tracker.update_tracking(
                    tracking_id, message="Calculating relationship similarity..."
                )
            relationship_score = self.calculate_relationship_similarity(
                entity1, entity2
            )
            components["relationship"] = relationship_score

            # Embedding similarity (if available)
            embedding_score = 0.0
            if "embedding" in entity1 and "embedding" in entity2:
                if tracking_id:
                    self.progress_tracker.update_tracking(
                        tracking_id, message="Calculating embedding similarity..."
                    )
                embedding_score = self.calculate_embedding_similarity(
                    entity1["embedding"], entity2["embedding"]
                )
                components["embedding"] = embedding_score

            # Weighted aggregation
            if tracking_id:
                self.progress_tracker.update_tracking(
                    tracking_id, message="Aggregating similarity scores..."
                )
            weights = {
                "string": self.string_weight,
                "property": self.property_weight,
                "relationship": self.relationship_weight,
                "embedding": self.embedding_weight if embedding_score > 0 else 0.0,
            }

            # Normalize weights
            total_weight = sum(w for k, w in weights.items() if k in components)
            if total_weight > 0:
                weights = {
                    k: w / total_weight for k, w in weights.items() if k in components
                }

            overall_score = sum(
                components.get(key, 0.0) * weight for key, weight in weights.items()
            )

            if tracking_id:
                self.progress_tracker.stop_tracking(
                    tracking_id,
                    status="completed",
                    message=f"Similarity score: {overall_score:.2f}",
                )
            return SimilarityResult(
                score=overall_score,
                method="multi_factor",
                components=components,
                metadata={"weights": weights},
            )

        except Exception as e:
            if tracking_id:
                self.progress_tracker.stop_tracking(
                    tracking_id, status="failed", message=str(e)
                )
            raise

    def calculate_string_similarity(
        self, str1: str, str2: str, method: str = "jaro_winkler"
    ) -> float:
        """
        Calculate string similarity between two strings.

        Args:
            str1: First string
            str2: Second string
            method: Similarity method ("levenshtein", "jaro_winkler", "cosine")

        Returns:
            Similarity score (0-1)
        """
        if not str1 or not str2:
            return 0.0

        str1_lower = str1.lower().strip()
        str2_lower = str2.lower().strip()

        if str1_lower == str2_lower:
            return 1.0

        if method == "levenshtein":
            return self._levenshtein_similarity(str1_lower, str2_lower)
        elif method == "jaro_winkler":
            return self._jaro_winkler_similarity(str1_lower, str2_lower)
        elif method == "cosine":
            return self._cosine_similarity(str1_lower, str2_lower)
        else:
            return self._levenshtein_similarity(str1_lower, str2_lower)

    def calculate_property_similarity(
        self, entity1: Dict[str, Any], entity2: Dict[str, Any]
    ) -> float:
        """
        Calculate similarity based on entity properties.

        Args:
            entity1: First entity
            entity2: Second entity

        Returns:
            Property similarity score (0-1)
        """
        props1 = entity1.get("properties", {})
        props2 = entity2.get("properties", {})

        if not props1 and not props2:
            return 1.0

        all_keys = set(props1.keys()) | set(props2.keys())
        if not all_keys:
            return 0.0

        matches = 0
        total = 0

        for key in all_keys:
            val1 = props1.get(key)
            val2 = props2.get(key)

            if val1 is None or val2 is None:
                # Missing value in one entity is not a mismatch, but lack of evidence
                # Assign neutral score (0.5) instead of 0.0
                matches += 0.5
                total += 1
                continue

            if isinstance(val1, str) and isinstance(val2, str):
                sim = self.calculate_string_similarity(str(val1), str(val2))
                matches += sim
            elif val1 == val2:
                matches += 1.0
            else:
                matches += 0.5  # Partial match

            total += 1

        return matches / total if total > 0 else 0.0

    def calculate_relationship_similarity(
        self, entity1: Dict[str, Any], entity2: Dict[str, Any]
    ) -> float:
        """
        Calculate similarity based on relationships.

        Args:
            entity1: First entity
            entity2: Second entity

        Returns:
            Relationship similarity score (0-1)
        """
        # Use pre-calculated hashable relationships if available
        if "_hashable_rels" in entity1:
            rels1 = entity1["_hashable_rels"]
        else:
            rels1 = set(self._make_hashable(r) for r in entity1.get("relationships", []))
            
        if "_hashable_rels" in entity2:
            rels2 = entity2["_hashable_rels"]
        else:
            rels2 = set(self._make_hashable(r) for r in entity2.get("relationships", []))

        if not rels1 and not rels2:
            return 0.5

        if not rels1 or not rels2:
            return 0.0

        intersection = rels1 & rels2
        union = rels1 | rels2

        return len(intersection) / len(union) if union else 0.0

    def _make_hashable(self, item: Any) -> Any:
        """Convert item to hashable form for set operations."""
        if isinstance(item, dict):
            return tuple(sorted((k, self._make_hashable(v)) for k, v in item.items()))
        if isinstance(item, list):
            return tuple(self._make_hashable(x) for x in item)
        return item

    def calculate_embedding_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity (0-1)
        """
        if len(embedding1) != len(embedding2):
            return 0.0

        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        magnitude1 = math.sqrt(sum(a * a for a in embedding1))
        magnitude2 = math.sqrt(sum(b * b for b in embedding2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        cosine_sim = dot_product / (magnitude1 * magnitude2)

        # Normalize to 0-1 range
        return (cosine_sim + 1) / 2

    def _levenshtein_similarity(self, s1: str, s2: str) -> float:
        """Calculate Levenshtein distance-based similarity."""
        if not s1 or not s2:
            return 0.0

        if s1 == s2:
            return 1.0

        distance = self._levenshtein_distance(s1, s2)
        max_len = max(len(s1), len(s2))

        return 1.0 - (distance / max_len) if max_len > 0 else 0.0

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _jaro_winkler_similarity(self, s1: str, s2: str) -> float:
        """Calculate Jaro-Winkler similarity."""
        if s1 == s2:
            return 1.0

        jaro = self._jaro_similarity(s1, s2)

        # Winkler prefix bonus
        prefix_len = 0
        min_len = min(len(s1), len(s2))
        for i in range(min_len):
            if s1[i] == s2[i]:
                prefix_len += 1
            else:
                break

        prefix_bonus = min(prefix_len, 4) * 0.1
        return jaro + prefix_bonus * (1 - jaro)

    def _jaro_similarity(self, s1: str, s2: str) -> float:
        """Calculate Jaro similarity."""
        if s1 == s2:
            return 1.0

        match_window = max(len(s1), len(s2)) // 2 - 1
        if match_window < 0:
            match_window = 0

        s1_matches = [False] * len(s1)
        s2_matches = [False] * len(s2)

        matches = 0
        transpositions = 0

        # Find matches
        for i in range(len(s1)):
            start = max(0, i - match_window)
            end = min(i + match_window + 1, len(s2))

            for j in range(start, end):
                if s2_matches[j] or s1[i] != s2[j]:
                    continue
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break

        if matches == 0:
            return 0.0

        # Count transpositions
        k = 0
        for i in range(len(s1)):
            if not s1_matches[i]:
                continue
            while not s2_matches[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1

        jaro = (
            matches / len(s1)
            + matches / len(s2)
            + (matches - transpositions / 2) / matches
        ) / 3.0
        return jaro

    def _cosine_similarity(self, s1: str, s2: str) -> float:
        """Calculate cosine similarity based on character n-grams."""

        # Simple character bigram approach
        def get_bigrams(text):
            return set(text[i : i + 2] for i in range(len(text) - 1))

        bigrams1 = get_bigrams(s1)
        bigrams2 = get_bigrams(s2)

        if not bigrams1 and not bigrams2:
            return 1.0

        intersection = bigrams1 & bigrams2
        union = bigrams1 | bigrams2

        return len(intersection) / len(union) if union else 0.0

    def batch_calculate_similarity(
        self, entities: List[Dict[str, Any]], threshold: Optional[float] = None
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any], float]]:
        """
        Calculate similarity for all entity pairs in a batch.

        This method optimizes calculation by comparing only pairs that are likely
        to be similar using a blocking/indexing strategy.

        Args:
            entities: List of entity dictionaries
            threshold: Similarity threshold for filtering (default: self.similarity_threshold)

        Returns:
            List of (entity1, entity2, similarity) tuples
        """
        # Track batch similarity calculation
        tracking_id = self.progress_tracker.start_tracking(
            file=None,
            module="deduplication",
            submodule="SimilarityCalculator",
            message=f"Calculating similarity for {len(entities)} entities",
        )

        try:
            threshold = threshold or self.similarity_threshold
            results = []

            # Pre-process entities for faster comparison
            # 1. Pre-calculate hashable relationships
            # 2. Pre-calculate lowercase names
            # 3. Pre-calculate property sets
            processed_entities = []
            for entity in entities:
                # Handle both dicts and Entity objects
                if hasattr(entity, "__dict__"):
                    processed_entity = vars(entity).copy()
                elif isinstance(entity, dict):
                    processed_entity = entity.copy()
                else:
                    processed_entity = {"_original": entity}
                
                # Pre-calculate hashable relationships for Jaccard similarity
                # Handle both 'relationships' and 'metadata.relationships'
                rels = processed_entity.get("relationships")
                if rels is None and "metadata" in processed_entity:
                    rels = processed_entity["metadata"].get("relationships")
                
                if rels:
                    processed_entity["_hashable_rels"] = set(self._make_hashable(r) for r in rels)
                else:
                    processed_entity["_hashable_rels"] = set()
                
                # Pre-calculate lowercase name
                # Handle both 'name' and 'text' (used in Entity class)
                name = processed_entity.get("name") or processed_entity.get("text") or ""
                processed_entity["_lower_name"] = name.lower().strip()
                
                processed_entities.append(processed_entity)

            # Blocking strategy: Group entities by first character of name
            # This significantly reduces the number of pairs to compare while
            # still catching most duplicates.
            blocks: Dict[str, List[int]] = {}
            for idx, entity in enumerate(processed_entities):
                name = entity["_lower_name"]
                if not name:
                    block_key = "___empty___"
                else:
                    # Use the first character as the block key
                    block_key = name[0]
                
                if block_key not in blocks:
                    blocks[block_key] = []
                blocks[block_key].append(idx)

            # Calculate total potential pairs within blocks for progress tracking
            total_pairs = 0
            for block_indices in blocks.values():
                n = len(block_indices)
                total_pairs += n * (n - 1) // 2

            processed = 0
            # Update more frequently: every 1% or at least every 10 items
            if total_pairs <= 10:
                update_interval = 1
            else:
                update_interval = max(1, min(100, total_pairs // 100))
            
            self.progress_tracker.update_tracking(
                tracking_id,
                status="running",
                message=f"Comparing {total_pairs} pairs across {len(blocks)} blocks..."
            )
            
            # Compare entities within each block
            for block_key, indices in blocks.items():
                for i_idx in range(len(indices)):
                    for j_idx in range(i_idx + 1, len(indices)):
                        i = indices[i_idx]
                        j = indices[j_idx]
                        
                        similarity = self.calculate_similarity(processed_entities[i], processed_entities[j], track=False)

                        if similarity.score >= threshold:
                            results.append((entities[i], entities[j], similarity.score))
                        
                        processed += 1
                        if processed % update_interval == 0 or processed == total_pairs:
                            self.progress_tracker.update_progress(
                                tracking_id,
                                processed=processed,
                                total=total_pairs,
                                message=f"Comparing pairs in block '{block_key}'... {processed}/{total_pairs}"
                            )

            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message=f"Found {len(results)} similar pairs across {len(blocks)} blocks",
            )
            return results

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise
